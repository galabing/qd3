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
    - delay_window (defines delay in months in model training, default 0 no
      delay)
    - max_neg (default 0)
    - min_pos (default 0)
    - min_date (default '0000-00-00')
    - max_date (default '9999-99-99')

    TODO: start_date and end_date are hand picked for now but can be automated.
"""

from config import *
from sklearn.metrics import *
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
    'delay_window': 0,
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

# Get model base name.
def getModelName(config_map):
  pos = config_map['model_spec'].find('(')
  assert pos > 0
  return config_map['model_spec'][:pos]

# Path to a specific model.
def getModelPath(model_dir, date, config_map):
  model = getModelName(config_map)
  return '%s/%s-%s-%d' % (model_dir, model, date, config_map['train_window'])

# Dir of prediction results.
def getResultDir(expeirment_dir):
  return '%s/results' % expeirment_dir

# Path to the result file -- since we only support one version of models
# the name is simply 'result'.
def getResultPath(result_dir):
  return '%s/result' % result_dir

# Dir of analysis.
def getAnalyzeDir(experiment_dir):
  return '%s/analyze' % experiment_dir

# Path to training stats.
def getStatsPath(experiment_dir, config_map):
  model = getModelName(config_map)
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

def evaluateModel(model_file, data_file, label_file):
  with open(model_file, 'rb') as fp:
    model = pickle.load(fp)
  X = numpy.loadtxt(data_file)
  y = numpy.loadtxt(label_file)
  p = model.predict(X)

  result = dict()
  result['f1'] = f1_score(y, p)
  result['auc'] = roc_auc_score(y, p)

  yp = [[y[i], p[i]] for i in range(X.shape[0])]
  yp.sort(key=lambda item: item[1], reverse=True)

  recall_denom = sum(y)
  for perc in [1, 10, 100]:
    end = int(X.shape[0] * perc / 100)
    assert end > 0
    num = 0.0
    for i in range(end):
      if yp[i][0] > 0.5:
        num += 1
    precision = num / end
    recall = num / recall_denom
    result['%dperc-precision' % perc] = precision
    result['%dperc-recall' % perc] = recall

  return result

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
    # Keep in sync with evaluateModel().
    print >> fp, '\t'.join([
        'date',
        'f1',
        'auc',
        '1perc-precision',
        '1perc-recall',
        '10perc-precision',
        '10perc-recall',
        '100perc-precision',
        '100perc-recall',
    ])
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
      result = evaluateModel(model_file, TMP_DATA_FILE, TMP_LABEL_FILE)
      # Keep in sync with evaluateModel().
      print >> fp, '\t'.join([
          date,
          '%.4f' % result['f1'],
          '%.4f' % result['auc'],
          '%.4f' % result['1perc-precision'],
          '%.4f' % result['1perc-recall'],
          '%.4f' % result['10perc-precision'],
          '%.4f' % result['10perc-recall'],
          '%.4f' % result['100perc-precision'],
          '%.4f' % result['100perc-recall'],
      ])
      fp.flush()

def predict(experiment_dir, config_map):
  result_dir = getResultDir(experiment_dir)
  util.maybeMakeDir(result_dir)
  result_file = getResultPath(result_dir)

  data_dir = getDataDir(experiment_dir)
  data_file = getDataPath(data_dir)
  label_file = getLabelPath(data_dir)
  meta_file = getMetaPath(data_dir)
  model_dir = getModelDir(experiment_dir)

  model_prefix = '%s-' % getModelName(config_map)
  model_suffix = '-%d' % config_map['train_window']

  cmd = ('%s/predict_all.py --data_file=%s --label_file=%s '
         '--meta_file=%s --model_dir=%s --model_prefix="%s" '
         '--model_suffix="%s" --prediction_window=%d '
         '--delay_window=%d --result_file=%s' % (
            CODE_DIR, data_file, label_file, meta_file,
            model_dir, model_prefix, model_suffix,
            config_map['predict_window'],
            config_map['delay_window'], result_file))
  util.run(cmd)

def analyze(experiment_dir, config_map):
  analyze_dir = getAnalyzeDir(experiment_dir)
  util.maybeMakeDir(analyze_dir)
  result_dir = getResultDir(experiment_dir)
  result_file = getResultPath(result_dir)
  cmd = ('%s/analyze_all.py --result_file=%s --hold_period=%d '
         '--analyze_dir=%s' % (
            CODE_DIR, result_file, config_map['predict_window'],
            analyze_dir))
  util.run(cmd)

def runExperiment(config_file):
  assert config_file.endswith(CONFIG_SUFFIX)
  pos = config_file.rfind('/')
  assert pos > 0
  experiment = config_file[pos+1:-len(CONFIG_SUFFIX)]
  experiment_dir = '%s/%s' % (EXPERIMENT_BASE_DIR, experiment)
  util.maybeMakeDir(experiment_dir)
  config_map = getConfig(config_file)

  makeFeatureList(experiment_dir, config_map)

  step = '%s_collect_data' % experiment
  if not util.checkDone(step):
    collectData(experiment_dir, config_map)
    util.markDone(step)

  step = '%s_train_models' % experiment
  if not util.checkDone(step):
    trainModels(experiment_dir, config_map)
    util.markDone(step)

  step = '%s_predict' % experiment
  if not util.checkDone(step):
    predict(experiment_dir, config_map)
    util.markDone(step)

  analyze(experiment_dir, config_map)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', required=True)
  args = parser.parse_args()
  util.configLogging()
  runExperiment(args.config)

if __name__ == '__main__':
  main()

