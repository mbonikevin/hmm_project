"""
turns sensor logger exports into the csv files the notebook reads.

point it at the folder holding your exports, either the zips or the unzipped folders.
each recording has to be named like walking_kevin_01 in the app, and the app needs
Accelerometer, Gravity and Gyroscope switched on.

usage: python convert_all.py <folder> [train|test]
"""

import os
import re
import sys
import glob
import shutil
import zipfile
import tempfile
import pandas as pd

RATE = 50
ACTIVITIES = ["standing", "walking", "jumping", "still"]
SENSORS = [("Accelerometer.csv", "a"), ("Gravity.csv", "r"), ("Gyroscope.csv", "g")]


def read_sensor(folder, filename, prefix):
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return None

    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    time_col = "seconds_elapsed" if "seconds_elapsed" in df.columns else "time"

    out = pd.DataFrame({"time": df[time_col].astype(float)})
    for axis in "xyz":
        out[prefix + axis] = df[axis].astype(float)
    return out.sort_values("time")


def convert(folder, out_path):
    frames = []
    for filename, prefix in SENSORS:
        df = read_sensor(folder, filename, prefix)
        if df is None:
            return "no " + filename + ", switch that sensor on in the app"
        frames.append(df)

    df = frames[0]
    for other in frames[1:]:
        df = pd.merge_asof(df, other, on="time", direction="nearest")

    df["time"] -= df["time"].iloc[0]
    df = df.set_index(pd.to_timedelta(df["time"], unit="s")).drop(columns="time")
    df = df.resample("%dms" % (1000 // RATE)).mean().interpolate().dropna()
    df.insert(0, "time", df.index.total_seconds())

    if len(df) < 70:
        return "too short, only %d rows" % len(df)

    df.to_csv(out_path, index=False)
    return None


def clean_name(raw):
    name = raw.lower().replace(" ", "_").replace(".zip", "")
    return re.sub(r"-\d{4}-\d{2}-\d{2}.*$", "", name)      # drop the timestamp


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root, split = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "train"

    out_dir = os.path.join("data", split)
    os.makedirs(out_dir, exist_ok=True)

    items = [p for p in sorted(glob.glob(os.path.join(root, "*")))
             if os.path.isdir(p) or p.endswith(".zip")]
    done, skipped = 0, []

    for item in items:
        name = clean_name(os.path.basename(item))
        if not any(name.startswith(a) for a in ACTIVITIES):
            continue

        folder = None
        if item.endswith(".zip"):
            folder = tempfile.mkdtemp()
            with zipfile.ZipFile(item) as z:
                z.extractall(folder)

        problem = convert(folder or item, os.path.join(out_dir, name + ".csv"))
        if folder:
            shutil.rmtree(folder)

        if problem:
            skipped.append((name, problem))
        else:
            done += 1

    print("wrote", done, "files into", out_dir)
    for name, why in skipped:
        print("skipped", name, "-", why)


if __name__ == "__main__":
    main()
