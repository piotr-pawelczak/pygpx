import math
from datetime import datetime

from pydantic import BaseModel

from pygpx.constants import EARTH_RADIUS_KM


class Coordinates(BaseModel):
    """Geographic coordinates as a latitude/longitude pair."""

    latitude: float
    longitude: float

    def distance_to(self, other: "Coordinates") -> float:
        """Compute the distance to another coordinate using the Haversine formula.

        Args:
            other: The target coordinates.

        Returns:
            Distance in kilometres.
        """
        coords = [self.latitude, self.longitude, other.latitude, other.longitude]
        lat_1, lon_1, lat_2, lon_2 = map(math.radians, coords)
        diff_lat = lat_2 - lat_1
        diff_lon = lon_2 - lon_1

        a = math.sin(diff_lat / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(diff_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        return c * EARTH_RADIUS_KM


class TrackPoint(BaseModel):
    """A single recorded point on a GPS track."""

    coordinates: Coordinates
    elevation: float | None = None
    timestamp: datetime | None = None
    heart_rate: int | None = None
    temperature: float | None = None


class TrackSegment(BaseModel):
    """A continuous sequence of track points within a track."""

    points: list[TrackPoint]

    def calculate_distance(self) -> float:
        """Compute the total distance covered across all points in this segment.

        Returns:
            Distance in kilometres, or 0.0 if the segment has fewer than two points.
        """
        if not self.points:
            return 0.0

        previous_coords = self.points[0].coordinates
        distance = 0.0
        for point in self.points[1:]:
            current_coords = point.coordinates
            distance += previous_coords.distance_to(current_coords)
            previous_coords = current_coords
        return distance


class Track(BaseModel):
    """A GPX track consisting of one or more segments."""

    name: str | None = None
    type: str | None = None
    segments: list[TrackSegment]
