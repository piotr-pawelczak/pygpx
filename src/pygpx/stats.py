from dataclasses import dataclass


@dataclass
class HeartRateStats:
    """Aggregated heart rate statistics for an activity."""

    min: int
    max: int
    avg: int


@dataclass
class ElevationStats:
    """Aggregated elevation statistics for an activity."""

    min: float
    max: float
    ascend: int
    descend: int


@dataclass
class VelocityStats:
    """Aggregated velocity statistics for an activity."""

    max: float
    average_total: float
    average_moving: float
