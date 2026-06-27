from pathlib import Path

from pygpx.parser import parse_gpx

PACKAGE_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
FILE_PATH = DATA_DIR / "ride.gpx"


def main():
    tracks = parse_gpx(FILE_PATH)
    track = tracks[0]
    print(len(track.segments))


if __name__ == "__main__":
    main()
