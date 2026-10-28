# human activity recognition with a hidden markov model

accelerometer and gyroscope data from a phone, four activities: standing, walking, jumping,
still. features go into a hidden markov model written from scratch with numpy.

## layout

```
data/train/   training csv files
data/test/    separate session, never used in training
videos/       5 second clip of each activity
figures/      plots saved by the notebook
report/       report and results table
hmm_activity.ipynb        the pipeline
prepare_sensor_logger.py  sensor logger export -> our csv format
```

## data format

one csv per recording named `activity_person_number.csv`, like `walking_kan_01.csv`. the
activity has to come first because the label is read from the file name.

columns: `time, ax, ay, az, gx, gy, gz`. everything is recorded at 50 hz.

## run

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook hmm_activity.ipynb
```

## collecting

record 5 to 10 seconds per sample at 50 hz, about 20 samples per activity across the group,
then export and run:

```
python prepare_sensor_logger.py <export folder> walking kan train
```

use `test` instead of `train` for the second session.
