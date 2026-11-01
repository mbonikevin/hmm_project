# human activity recognition with a hidden markov model

accelerometer, gravity and gyroscope data from two phones, four activities: standing, walking,
jumping, still. a hidden markov model written from scratch with numpy decodes the activity.

trained on 80 recordings made in the living room, tested on 24 recordings made later in the
bedroom. overall accuracy on that unseen session is 95.1 percent.

## layout

```
data/raw/     the untouched sensor logger exports
data/train/   80 training recordings, living room
data/test/    24 test recordings, bedroom, never used in training
videos/       one clip per activity
figures/      plots saved by the notebook
report/       the report and the results table
hmm_activity.ipynb   the pipeline
convert_all.py       sensor logger export -> our csv files
```

## data format

one csv per recording named `activity_person_number.csv`, like `walking_kevin_01.csv`. the
activity has to come first because the label is read from the file name.

columns: `time, ax, ay, az, rx, ry, rz, gx, gy, gz`, where `a` is acceleration, `r` is gravity
and `g` is gyroscope. everything is on a 50 hz grid.

## run

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook hmm_activity.ipynb
```

## collecting more data

in sensor logger, switch on **accelerometer, gravity and gyroscope**, set the rate to 50 hz,
and name each recording like `walking_kevin_01` before exporting. the gravity sensor matters,
without it the notebook has no tilt information and standing and still become hard to tell
apart.

record 5 to 10 seconds per sample, export as csv, then:

```
python convert_all.py ~/Downloads/your-export-folder train
```

use `test` instead of `train` for a separate session. the script reads zips or unzipped
folders and prints anything it skipped.

## rebuilding the csv files

the raw exports are kept, so everything in `data/train` and `data/test` can be regenerated:

```
python convert_all.py data/raw/train train
python convert_all.py data/raw/test test
```
