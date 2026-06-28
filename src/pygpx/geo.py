from itertools import pairwise

from pygpx.constants import DistanceUnit
from pygpx.models import Track, TrackSegment


def calculate_segment_distance(segment: TrackSegment, unit: DistanceUnit = DistanceUnit.KM) -> float:
    """Compute the total distance covered across all points in a segment.

    Args:
        segment: The track segment to measure.
        unit: The distance unit to use (default: km).

    Returns:
        Distance in the specified unit, or 0.0 if the segment has fewer than two points.
    """
    return sum(
        a.coordinates.distance_to(b.coordinates, unit)
        for a, b in pairwise(segment.points)
    )


def calculate_total_distance(tracks: list[Track], unit: DistanceUnit = DistanceUnit.KM) -> float:
    """Compute the total distance covered across all tracks and their segments.

    Args:
        tracks: List of tracks to measure.
        unit: The distance unit to use (default: km).

    Returns:
        Total distance in the specified unit.
    """
    return sum(
        calculate_segment_distance(segment, unit)
        for track in tracks
        for segment in track.segments
    )
