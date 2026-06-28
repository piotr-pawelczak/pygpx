from pathlib import Path
from typing import TypeAlias
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from pygpx.constants import GpxTag
from pygpx.models import Coordinates, Track, TrackPoint, TrackSegment

Namespaces: TypeAlias = dict[str, str]


def _get_namespaces(file_path: Path) -> Namespaces:
    """Extract XML namespace mappings from a GPX file.

    Args:
        file_path: Path to the GPX file to extract namespaces from.

    Returns:
        A dictionary mapping namespace prefixes to their URIs.
    """
    namespaces = {}
    for _, data in ElementTree.iterparse(file_path, events=("start-ns",)):
        prefix, uri = data
        namespaces[prefix] = uri
    return namespaces


def parse_point(point: Element, ns: Namespaces) -> TrackPoint:
    """Parse a single GPX track point element into a TrackPoint model.

    Args:
        point: XML element representing a single track point (trkpt).
        ns: Namespace map extracted from the GPX file.

    Returns:
        A TrackPoint instance populated with the point's data.

    Raises:
        ValidationError: If required fields (lat, lon) are missing or invalid.
    """
    return TrackPoint(
        coordinates=Coordinates(
            latitude=point.get(GpxTag.LATITUDE),  # type: ignore
            longitude=point.get(GpxTag.LONGITUDE),  # type: ignore
        ),
        elevation=point.findtext(
            GpxTag.ELEVATION, namespaces=ns
        ),  # ty: ignore[invalid-argument-type]
        timestamp=point.findtext(
            GpxTag.TIMESTAMP, namespaces=ns
        ),  # ty: ignore[invalid-argument-type]
        temperature=point.findtext(
            GpxTag.TEMPERATURE, namespaces=ns
        ),  # ty: ignore[invalid-argument-type]
        heart_rate=point.findtext(
            GpxTag.HEART_RATE, namespaces=ns
        ),  # ty: ignore[invalid-argument-type]
    )


def parse_segment(segment: Element, ns: Namespaces) -> TrackSegment:
    """Parse a single GPX track segment element into a TrackSegment model.

    Args:
        segment: XML element representing a track segment (trkseg).
        ns: Namespace map extracted from the GPX file.

    Returns:
        A TrackSegment instance containing all parsed track points.
    """
    points = segment.findall(GpxTag.TRACK_POINT, ns)
    return TrackSegment(points=[parse_point(p, ns) for p in points])


def parse_track(track: Element, ns: Namespaces) -> Track:
    """Parse a single GPX track element into a Track model.

    Args:
        track: XML element representing a track (trk).
        ns: Namespace map extracted from the GPX file.

    Returns:
        A Track instance containing all parsed segments and metadata.
    """
    name = track.findtext(GpxTag.TRACK_NAME, namespaces=ns)
    activity_type = track.findtext(GpxTag.ACTIVITY_TYPE, namespaces=ns)
    segments = track.findall(GpxTag.TRACK_SEGMENT, ns)
    return Track(
        name=name,
        type=activity_type,
        segments=[parse_segment(segment, ns) for segment in segments],
    )


def parse_gpx(file_path: Path) -> list[Track]:
    """Parse a GPX file into a list of Track models.

    Args:
        file_path: Path to the GPX file to parse.

    Returns:
        A list of Track instances parsed from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ParseError: If the file is not valid XML.
        ValidationError: If any track point contains invalid data.
    """
    ns = _get_namespaces(file_path)
    gpx_tree = ElementTree.parse(file_path)
    root = gpx_tree.getroot()

    tracks = root.findall(GpxTag.TRACK, ns)
    gpx = [parse_track(track, ns) for track in tracks]

    return gpx
