GPX_NS = "http://www.topografix.com/GPX/1/1"
GPXTPX_NS = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"


def gpx_tag(tag: str) -> str:
    return f"{{{GPX_NS}}}{tag}"


def gpxtpx_tag(tag: str) -> str:
    return f"{{{GPXTPX_NS}}}{tag}"
