"""
sensor logger export -> one csv with time, ax, ay, az, gx, gy, gz

usage: python prepare_sensor_logger.py <export folder> <activity> <person> [train|test]
"""

import os
import sys
import glob
import pandas as pd

RATE = 50


def read_sensor(folder, keyword, prefix):
    path = next((p for p in glob.glob(os.path.join(folder, "*.csv"))
                 if keyword in os.path.basename(p).lower()), None)
    if path is None:
        sys.exit("no " + keyword + " file in " + folder)

    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    time_col = "seconds_elapsed" if "seconds_elapsed" in df.columns else "time"

    out = pd.DataFrame({"time": df[time_col].astype(float)})
    for axis in "xyz":
        out[prefix + axis] = df[axis].astype(float)
    return out.sort_values("time")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    folder, activity, person = sys.argv[1:4]
    split = sys.argv[4] if len(sys.argv) > 4 else "train"

    acc = read_sensor(folder, "accelerometer", "a")
    gyro = read_sensor(folder, "gyroscope", "g")
    df = pd.merge_asof(acc, gyro, on="time", direction="nearest")

    # fixed grid so recordings from different phones line up
    df["time"] -= df["time"].iloc[0]
    df = df.set_index(pd.to_timedelta(df["time"], unit="s")).drop(columns="time")
    df = df.resample("%dms" % (1000 // RATE)).mean().interpolate().dropna()
    df.insert(0, "time", df.index.total_seconds())

    out_dir = os.path.join("data", split)
    os.makedirs(out_dir, exist_ok=True)
    n = len(glob.glob(os.path.join(out_dir, "%s_%s_*.csv" % (activity, person)))) + 1
    path = os.path.join(out_dir, "%s_%s_%02d.csv" % (activity, person, n))

    df.to_csv(path, index=False)
    print("wrote", path, len(df), "rows")


if __name__ == "__main__":
    main()
