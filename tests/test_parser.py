from datetime import UTC, datetime
from pathlib import Path
from xml.etree.ElementTree import Element, ParseError

import pytest
from pydantic import ValidationError

from pygpx.models import Track, TrackPoint, TrackSegment
from pygpx.parser import parse_gpx, parse_point, parse_segment, parse_track
from tests.helpers import gpx_tag


class TestParsePoint:
    def test_full(self, make_point_element, namespaces):
        # given
        point = make_point_element(
            elevation="229.6",
            timestamp="2026-06-16T14:46:57Z",
            heart_rate="130",
            temperature="23",
        )

        # when
        result = parse_point(point, namespaces)

        # then
        assert isinstance(result, TrackPoint)
        assert result.coordinates.latitude == pytest.approx(50.00747)
        assert result.coordinates.longitude == pytest.approx(19.957913)
        assert result.elevation == pytest.approx(229.6)
        assert result.timestamp == datetime(2026, 6, 16, 14, 46, 57, tzinfo=UTC)
        assert result.heart_rate == 130
        assert result.temperature == pytest.approx(23.0)

    def test_minimal(self, make_point_element, namespaces):
        # given
        point = make_point_element()

        # when
        result = parse_point(point, namespaces)

        # then
        assert result.coordinates.latitude == pytest.approx(50.00747)
        assert result.coordinates.longitude == pytest.approx(19.957913)
        assert result.elevation is None
        assert result.timestamp is None
        assert result.heart_rate is None
        assert result.temperature is None

    def test_custom_coordinates(self, make_point_element, namespaces):
        # given
        point = make_point_element(lat="48.8566", lon="2.3522")

        # when
        result = parse_point(point, namespaces)

        # then
        assert result.coordinates.latitude == pytest.approx(48.8566)
        assert result.coordinates.longitude == pytest.approx(2.3522)

    def test_missing_lat_lon_raises(self, namespaces):
        # given
        point = Element(gpx_tag("trkpt"))

        # when / then
        with pytest.raises(ValidationError):
            parse_point(point, namespaces)

    def test_invalid_lat_lon_raises(self, make_point_element, namespaces):
        # given
        point = make_point_element(lat="not_a_number", lon="not_a_number")

        # when / then
        with pytest.raises(ValidationError):
            parse_point(point, namespaces)


class TestParseSegment:
    def test_with_single_point(
        self, make_segment_element, make_point_element, namespaces
    ):
        # given
        segment = make_segment_element(points=[make_point_element()])

        # when
        result = parse_segment(segment, namespaces)

        # then
        assert isinstance(result, TrackSegment)
        assert len(result.points) == 1

    def test_with_multiple_points(self, make_segment_element, namespaces):
        # given
        segment = make_segment_element()

        # when
        result = parse_segment(segment, namespaces)

        # then
        assert isinstance(result, TrackSegment)
        assert len(result.points) == 2

    def test_empty(self, make_segment_element, namespaces):
        # given
        segment = make_segment_element(points=[])

        # when
        result = parse_segment(segment, namespaces)

        # then
        assert isinstance(result, TrackSegment)
        assert result.points == []

    def test_point_content(self, make_segment_element, make_point_element, namespaces):
        # given
        segment = make_segment_element(
            points=[make_point_element(lat="48.8566", lon="2.3522", elevation="35.0")]
        )

        # when
        result = parse_segment(segment, namespaces)

        # then
        point = result.points[0]
        assert point.coordinates.latitude == pytest.approx(48.8566)
        assert point.coordinates.longitude == pytest.approx(2.3522)
        assert point.elevation == pytest.approx(35.0)


class TestParseTrack:
    def test_full(self, make_track_element, namespaces):
        # given
        track = make_track_element()

        # when
        result = parse_track(track, namespaces)

        # then
        assert isinstance(result, Track)
        assert result.name == "Afternoon Ride"
        assert result.type == "cycling"
        assert len(result.segments) == 1

    def test_without_name_and_type(self, make_track_element, namespaces):
        # given
        track = make_track_element(name=None, activity_type=None)

        # when
        result = parse_track(track, namespaces)

        # then
        assert result.name is None
        assert result.type is None
        assert len(result.segments) == 1

    def test_with_multiple_segments(
        self, make_track_element, make_segment_element, namespaces
    ):
        # given
        track = make_track_element(
            segments=[make_segment_element(), make_segment_element()]
        )

        # when
        result = parse_track(track, namespaces)

        # then
        assert len(result.segments) == 2

    def test_segment_content(
        self, make_track_element, make_segment_element, make_point_element, namespaces
    ):
        # given
        track = make_track_element(
            segments=[
                make_segment_element(
                    points=[make_point_element(lat="48.8566", lon="2.3522")]
                )
            ]
        )

        # when
        result = parse_track(track, namespaces)

        # then
        point = result.segments[0].points[0]
        assert point.coordinates.latitude == pytest.approx(48.8566)
        assert point.coordinates.longitude == pytest.approx(2.3522)


class TestParseGpx:
    def test_returns_tracks(self, ride_gpx_path: Path):
        # given
        file_path = ride_gpx_path

        # when
        result = parse_gpx(file_path)

        # then
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Track)

    def test_track_metadata(self, ride_gpx_path: Path):
        # given
        file_path = ride_gpx_path

        # when
        result = parse_gpx(file_path)

        # then
        track = result[0]
        assert track.name == "Wola Radziszowska"
        assert track.type == "cycling"

    def test_points_accessible(self, ride_gpx_path: Path):
        # given
        file_path = ride_gpx_path

        # when
        result = parse_gpx(file_path)

        # then
        point = result[0].segments[0].points[0]
        assert isinstance(point, TrackPoint)
        assert point.coordinates.latitude == pytest.approx(50.00747)
        assert point.coordinates.longitude == pytest.approx(19.957913)

    def test_file_not_found(self):
        # given
        file_path = Path("/non/existent/file.gpx")

        # when / then
        with pytest.raises(FileNotFoundError):
            parse_gpx(file_path)

    def test_invalid_xml_raises(self, invalid_xml_path: Path):
        # given
        file_path = invalid_xml_path

        # when / then
        with pytest.raises(ParseError):
            parse_gpx(file_path)
