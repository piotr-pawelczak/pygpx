from pathlib import Path

from pygpx.activity import Activity

PACKAGE_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
FILE_PATH = DATA_DIR / "ride.gpx"


def main():
    activity = Activity(FILE_PATH)
    print(activity.get_elapsed_time())
    print(activity.get_moving_time())
    print(activity.get_velocity_stats())


if __name__ == "__main__":
    main()
