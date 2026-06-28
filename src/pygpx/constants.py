from enum import StrEnum


class GpxTag(StrEnum):
    TRACK = "trk"
    TRACK_SEGMENT = "trkseg"
    TRACK_POINT = "trkpt"
    # Track Children
    TRACK_NAME = "name"
    ACTIVITY_TYPE = "type"
    # Track Point Children
    LATITUDE = "lat"
    LONGITUDE = "lon"
    ELEVATION = "ele"
    TIMESTAMP = "time"
    TEMPERATURE = ".//gpxtpx:atemp"
    HEART_RATE = ".//gpxtpx:hr"


class DistanceUnit(StrEnum):
    KM = "km"
    MILES = "miles"


EARTH_RADIUS_KM = 6371
EARTH_RADIUS_MILES = 3958.8

MOVING_TIME_KM_PER_HOUR_THRESHOLD = 0.5
MOVING_TIME_MILES_PER_HOUR_THRESHOLD = 0.3

SECONDS_IN_HOUR = 3600
