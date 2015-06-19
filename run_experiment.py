#!/usr/bin/python

""" Runs one experiment.
    Example usage:
      ./run_experiment.py --config=./config.json

    The config specifies:
    - features (eg, 'sf1 + eod + eod-R3000 + sector')
    - label_suffix (eg, 'yahoo/egain10/12/R3000')
    - start_date (eg, '200412')
    - end_date (eg, '201305')
    - model_spec (default
      'RandomForestClassifier(n_estimators=100, max_depth=2)')
    - feature_window (defines max lag in days in joining features, default 120)
    - train_window (defines training period in months, default -1 using entire
      history)
    - train_perc (default 1.0)
    - predict_window (defines prediction window in months, default 12)
    - max_neg (default 0)
    - min_pos (default 0)
    - min_date (default '0000-00-00')
    - max_date (default '9999-99-99')

    TODO: start_date and end_date are hand picked for now but can be automated.
"""

from config import *
import argparse
import config
import json
import numpy
import os
import pickle
import util

CONFIG_SUFFIX = '.json'
TMP_DATA_FILE = '/tmp/qd2_tmp_data'
TMP_LABEL_FILE = '/tmp/qd2_tmp_label'

REQUIRED_FIELDS = [
    'features',
    'label_suffix',
    'start_date',
    'end_date',
]
DEFAULT_VALUES = {
    'model_spec': 'RandomForestClassifier(n_estimators=100, max_depth=2)',
    'feature_window': 120,
    'train_window': -1,
    'train_perc': 1.0,
    'predict_window': 12,
    'max_neg': 0.0,
    'min_pos': 0.0,
    'min_date': '0000-00-00',
    'max_date': '9999-99-99',
    'min_feature_perc': 0.8,
}

def getConfig(config_file):
  with open(config_file, 'r') as fp:
    config_map = json.load(fp)
  for field in REQUIRED_FIELDS:
    assert field in config_map, 'missing field %s in config' % field
  for field, value in DEFAULT_VALUES.iteritems():
    if field not in config_map:
      config_map[field] = value
  return config_map

def getFeatureListPath(experiment_dir):
  return '%s/feature_list' % experiment_dir

# Dir of label SOURCE data (egain dir).
# This is not the dir to training labels (getLabelPath()).
def getLabelDir(label_suffix):
  return '%s/%s' % (RUN_DIR, label_suffix)

# Dir of training data/label/meta files.
def getDataDir(experiment_dir):
  return '%s/data' % experiment_dir

# Path to training data.
def getDataPath(data_dir):
  return '%s/data' % data_dir

# Path to training labels.
def getLabelPath(data_dir):
  return '%s/label' % data_dir

# Path to training metadata.
def getMetaPath(data_dir):
  return '%s/meta' % data_dir

# Path to training weights.
def getWeightPath(data_dir):
  return '%s/weight' % data_dir

# Dir of trained models.
def getModelDir(experiment_dir):
  return '%s/models' % experiment_dir

# Path to a specific model.
def getModelPath(model_dir, date, config_map):
  pos = config_map['model_spec'].find('(')
  assert pos > 0
  model = config_map['model_spec'][:pos]
  return '%s/%s-%s-%d' % (model_dir, model, date, config_map['train_window'])

# Dir of prediction results.
def getResultDir(expeirment_dir):
  return '%s/results' % expeirment_dir

# Path to training stats.
def getStatsPath(experiment_dir, config_map):
  pos = config_map['model_spec'].find('(')
  assert pos > 0
  model = config_map['model_spec'][:pos]
  return '%s/%s-stats.tsv' % (experiment_dir, model)

def makeFeatureList(experiment_dir, config_map):
  features = [item.strip() for item in config_map['features'].split('+')]
  with open(getFeatureListPath(experiment_dir), 'w') as ofp:
    for feature in features:
      with open('%s/%s' % (FEATURE_LIST_DIR, feature), 'r') as ifp:
        lines = ifp.read().splitlines()
      for line in lines:
        if not line.startswith('#'):
          print >> ofp, line

def collectData(experiment_dir, config_map):
  data_dir = getDataDir(experiment_dir)
  util.maybeMakeDir(data_dir)

  gain_dir = getLabelDir(config_map['label_suffix'])
  feature_list = getFeatureListPath(experiment_dir)
  data_file = getDataPath(data_dir)
  label_file = getLabelPath(data_dir)
  meta_file = getMetaPath(data_dir)
  weight_file = getWeightPath(data_dir)

  cmd = ('%s/collect_cls_data.py --gain_dir=%s --max_neg=%f --min_pos=%f '
         '--feature_base_dir=%s --feature_list=%s --feature_stats=%s '
         '--min_date=%s --max_date=%s --window=%d --min_feature_perc=%f '
         '--data_file=%s --label_file=%s --meta_file=%s --weight_file=%s' % (
            CODE_DIR, gain_dir, config_map['max_neg'], config_map['min_pos'],
            FEATURE_DIR, feature_list, FEATURE_STATS_FILE,
            config_map['min_date'], config_map['max_date'],
            config_map['feature_window'], config_map['min_feature_perc'],
            data_file, label_file, meta_file, weight_file))
  util.run(cmd)

def computeClsError(model_file, data_file, label_file):
  with open(model_file, 'rb') as fp:
    model = pickle.load(fp)
  X = numpy.loadtxt(data_file)
  y = numpy.loadtxt(label_file)

  p = model.predict(X)
  tp, tn, fp, fn = 0.0, 0.0, 0.0, 0.0
  for i in range(X.shape[0]):
    positive = p[i] > 0.5
    if positive:
      if y[i] > 0.5:
        tp += 1
      else:
        fp += 1
    else:
      if y[i] > 0.5:
        fn += 1
      else:
        tn += 1
  accuracy = (tp + tn) / (tp + tn + fp + fn)
  precision = tp / (tp + fp)
  recall = tp / (tp + fn)
  return accuracy, precision, recall

def trainModels(experiment_dir, config_map):
  dates = []
  date = config_map['start_date']
  while date <= config_map['end_date']:
    dates.append(date)
    year = int(date[:4])
    month = int(date[4:])
    if month < 12:
      month += 1
    else:
      month = 1
      year += 1
    date = '%04d%02d' % (year, month)

  data_dir = getDataDir(experiment_dir)
  data_file = getDataPath(data_dir)
  label_file = getLabelPath(data_dir)
  meta_file = getMetaPath(data_dir)

  model_dir = getModelDir(experiment_dir)
  util.maybeMakeDir(model_dir)

  stats_file = getStatsPath(experiment_dir, config_map)
  with open(stats_file, 'w') as fp:
    print >> fp, '\t'.join(['date', 'accuracy', 'precision', 'recall'])
    for date in dates:
      model_file = getModelPath(model_dir, date, config_map)
      cmd = ('%s/train_model.py --data_file=%s --label_file=%s --meta_file=%s '
             '--yyyymm=%s --months=%d --model_def="%s" --perc=%f --model_file=%s '
             '--tmp_data_file=%s --tmp_label_file=%s' % (
                CODE_DIR, data_file, label_file, meta_file, date,
                config_map['train_window'], config_map['model_spec'],
                config_map['train_perc'], model_file,
                TMP_DATA_FILE, TMP_LABEL_FILE))
      util.run(cmd)
      accuracy, precision, recall = computeClsError(
          model_file, TMP_DATA_FILE, TMP_LABEL_FILE)
      print >> fp, '\t'.join([
          date, '%.4f' % accuracy, '%.4f' % precision, '%.4f' % recall])
      fp.flush()

def runExperiment(config_file):
  assert config_file.endswith(CONFIG_SUFFIX)
  pos = config_file.rfind('/')
  assert pos > 0
  experiment = config_file[pos+1:-len(CONFIG_SUFFIX)]
  experiment_dir = '%s/%s' % (EXPERIMENT_BASE_DIR, experiment)
  util.maybeMakeDir(experiment_dir)
  config_map = getConfig(config_file)

  #makeFeatureList(experiment_dir, config_map)
  #collectData(experiment_dir, config_map)
  trainModels(experiment_dir, config_map)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', required=True)
  args = parser.parse_args()
  util.configLogging()
  runExperiment(args.config)

if __name__ == '__main__':
  main()

