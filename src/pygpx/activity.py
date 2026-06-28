from datetime import timedelta
from functools import cached_property
from itertools import pairwise
from pathlib import Path

from pygpx import parse_gpx
from pygpx.constants import (
    MOVING_TIME_KM_PER_HOUR_THRESHOLD,
    MOVING_TIME_MILES_PER_HOUR_THRESHOLD,
    SECONDS_IN_HOUR,
    DistanceUnit,
)
from pygpx.geo import calculate_total_distance
from pygpx.models import Track, TrackPoint
from pygpx.stats import ElevationStats, HeartRateStats, VelocityStats


class Activity:
    """Represents a parsed GPX activity and provides methods for computing stats."""

    def __init__(self, file_path: Path, unit: DistanceUnit = DistanceUnit.KM) -> None:
        """Parse a GPX file and initialise the activity.

        Args:
            file_path: Path to the GPX file to load.
            unit: Distance unit for velocity and distance calculations (default: km).
        """
        self._tracks: list[Track] = parse_gpx(file_path)
        self._unit = unit

    @cached_property
    def _all_points(self) -> tuple[TrackPoint, ...]:
        """All track points flattened across every track and segment.

        Returns:
            A tuple of TrackPoint instances in recording order.
        """
        points: list[TrackPoint] = []
        for track in self._tracks:
            for segment in track.segments:
                points.extend(segment.points)
        return tuple(points)

    @cached_property
    def _velocity_intervals(self) -> tuple[tuple[float, float], ...]:
        """Compute per-interval (velocity, time_seconds) pairs, skipping invalid ones.

        Intervals where either endpoint has no timestamp, or where elapsed time is zero,
        are excluded. Velocity unit matches the activity's configured distance unit.

        Returns:
            A tuple of (velocity, time_seconds) pairs.
        """
        points = self._all_points
        if not points:
            return ()

        intervals: list[tuple[float, float]] = []

        for previous_point, point in pairwise(points):
            if point.timestamp is None or previous_point.timestamp is None:
                continue

            time_seconds = (point.timestamp - previous_point.timestamp).total_seconds()
            if time_seconds == 0:
                continue

            distance = previous_point.coordinates.distance_to(
                point.coordinates, self._unit
            )
            velocity = distance / (time_seconds / SECONDS_IN_HOUR)
            intervals.append((velocity, time_seconds))

        return tuple(intervals)

    @property
    def _moving_time_threshold(self) -> float:
        """Velocity threshold below which the activity is considered stopped.

        Returns:
            Threshold in km/h or mph depending on configured unit.
        """
        return (
            MOVING_TIME_KM_PER_HOUR_THRESHOLD
            if self._unit == DistanceUnit.KM
            else MOVING_TIME_MILES_PER_HOUR_THRESHOLD
        )

    def get_heart_rate_stats(self) -> HeartRateStats | None:
        """Compute min, max and average heart rate across all points.

        Points without heart rate data are ignored. Returns None if no
        heart rate data is present.

        Returns:
            A HeartRateStats instance, or None.
        """
        heart_rates = [
            p.heart_rate for p in self._all_points if p.heart_rate is not None
        ]

        if not heart_rates:
            return None

        return HeartRateStats(
            min=min(heart_rates),
            max=max(heart_rates),
            avg=int(sum(heart_rates) / len(heart_rates)),
        )

    def get_elevation_stats(self) -> ElevationStats | None:
        """Compute elevation statistics across all points.

        Points without elevation data are ignored. Returns None if no
        elevation data is present.

        Returns:
            An ElevationStats instance with min/max in metres and ascend/descend
            as accumulated integers, or None.
        """
        elevations = [p.elevation for p in self._all_points if p.elevation is not None]

        if not elevations:
            return None

        min_elevation = max_elevation = previous_elevation = elevations[0]
        ascend = descend = 0.0

        for elevation in elevations[1:]:
            diff = elevation - previous_elevation
            if diff > 0:
                ascend += diff
            else:
                descend += abs(diff)
            previous_elevation = elevation

            if elevation < min_elevation:
                min_elevation = elevation
            elif elevation > max_elevation:
                max_elevation = elevation

        return ElevationStats(
            min=min_elevation,
            max=max_elevation,
            ascend=int(ascend),
            descend=int(descend),
        )

    def get_total_distance(self) -> float:
        """Compute total distance covered across all tracks and segments.

        Returns:
            Total distance in the configured unit (km or miles).
        """
        return calculate_total_distance(self._tracks, self._unit)

    def get_elapsed_time(self) -> timedelta:
        """Compute elapsed time from first to last recorded point.

        Returns timedelta(0) if there are no points or timestamps are missing.

        Returns:
            Elapsed time as a timedelta.
        """
        points = self._all_points
        if not points:
            return timedelta(0)

        start_time, end_time = points[0].timestamp, points[-1].timestamp
        if start_time is None or end_time is None:
            return timedelta(0)

        return end_time - start_time

    def get_velocities(self) -> list[float]:
        """Return the velocity for each valid recorded interval.

        Returns:
            A list of velocities in km/h or mph depending on configured unit.
        """
        return [v for v, _ in self._velocity_intervals]

    def get_moving_time(self) -> timedelta:
        """Compute moving time by summing intervals above the velocity threshold.

        The threshold depends on the configured distance unit.

        Returns:
            Moving time as a timedelta.
        """
        moving_time = sum(
            t for v, t in self._velocity_intervals if v > self._moving_time_threshold
        )
        return timedelta(seconds=moving_time)

    def get_velocity_stats(self) -> VelocityStats:
        """Compute velocity statistics for the activity.

        Returns:
            A VelocityStats instance with max, average_total and average_moving
            velocities in the configured unit (km/h or mph).
        """
        velocities = self.get_velocities()
        total_distance = self.get_total_distance()
        elapsed_time = self.get_elapsed_time().total_seconds() / SECONDS_IN_HOUR
        moving_time = self.get_moving_time().total_seconds() / SECONDS_IN_HOUR

        return VelocityStats(
            max=max(velocities),
            average_total=total_distance / elapsed_time,
            average_moving=total_distance / moving_time,
        )
