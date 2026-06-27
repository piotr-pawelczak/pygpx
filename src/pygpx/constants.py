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
