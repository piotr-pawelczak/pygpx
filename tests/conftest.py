import pytest
from pathlib import Path
from typing import Callable
from xml.etree.ElementTree import Element, SubElement

from pygpx.parser import Namespaces
from tests.helpers import gpx_tag, gpxtpx_tag


@pytest.fixture
def ride_gpx_path() -> Path:
    return Path(__file__).parent.parent / "data" / "ride.gpx"


@pytest.fixture
def namespaces() -> Namespaces:
    return {
        "": "http://www.topografix.com/GPX/1/1",
        "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
        "gpxx": "http://www.garmin.com/xmlschemas/GpxExtensions/v3",
    }


@pytest.fixture
def make_point_element():
    def factory(
        lat: str = "50.0074700",
        lon: str = "19.9579130",
        elevation: str | None = None,
        timestamp: str | None = None,
        heart_rate: str | None = None,
        temperature: str | None = None,
    ) -> Element:
        point = Element(gpx_tag("trkpt"), attrib={"lat": lat, "lon": lon})

        if elevation is not None:
            ele = SubElement(point, gpx_tag("ele"))
            ele.text = elevation

        if timestamp is not None:
            time = SubElement(point, gpx_tag("time"))
            time.text = timestamp

        if heart_rate is not None or temperature is not None:
            extensions = SubElement(point, gpx_tag("extensions"))
            tp_ext = SubElement(extensions, gpxtpx_tag("TrackPointExtension"))
            if heart_rate is not None:
                hr = SubElement(tp_ext, gpxtpx_tag("hr"))
                hr.text = heart_rate
            if temperature is not None:
                atemp = SubElement(tp_ext, gpxtpx_tag("atemp"))
                atemp.text = temperature

        return point

    return factory


@pytest.fixture
def make_segment_element(make_point_element: Callable[..., Element]) -> Callable[..., Element]:
    def factory(points: list[Element] | None = None) -> Element:
        segment = Element(gpx_tag("trkseg"))
        if points is None:
            points = [make_point_element(), make_point_element()]
        for point in points:
            segment.append(point)
        return segment

    return factory


@pytest.fixture
def make_track_element(make_segment_element):
    def factory(
        name: str | None = "Afternoon Ride",
        activity_type: str | None = "cycling",
        segments: list[Element] | None = None,
    ) -> Element:
        track = Element(gpx_tag("trk"))

        if name is not None:
            name_el = SubElement(track, gpx_tag("name"))
            name_el.text = name

        if activity_type is not None:
            type_el = SubElement(track, gpx_tag("type"))
            type_el.text = activity_type

        if segments is None:
            segments = [make_segment_element()]
        for segment in segments:
            track.append(segment)

        return track

    return factory
