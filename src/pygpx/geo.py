from itertools import pairwise

from pygpx.models import Track, TrackSegment


def calculate_segment_distance(segment: TrackSegment) -> float:
    """Compute the total distance covered across all points in a segment.

    Args:
        segment: The track segment to measure.

    Returns:
        Distance in kilometres, or 0.0 if the segment has fewer than two points.
    """
    return sum(
        a.coordinates.distance_to(b.coordinates)
        for a, b in pairwise(segment.points)
    )


def calculate_total_distance(tracks: list[Track]) -> float:
    """Compute the total distance covered across all tracks and their segments.

    Args:
        tracks: List of tracks to measure.

    Returns:
        Total distance in kilometres.
    """
    return sum(
        calculate_segment_distance(segment)
        for track in tracks
        for segment in track.segments
    )
