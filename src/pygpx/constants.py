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


EARTH_RADIUS_KM = 6371
MOVING_TIME_KM_PER_HOUR_THRESHOLD = 0.5
SECONDS_IN_HOUR = 3600
