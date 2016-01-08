#!/usr/bin/python2.7

# Adapted from qd.
""" Collects data for classification/regression experiments.

    Example usage:
      ./collect_data.py --gain_dir=./gains/1
                        --date_file=./dates
                        --max_neg=0.01
                        --min_pos=0.01
                        --feature_base_dir=./features
                        --feature_list=./feature_list
                        --feature_stats=./feature_stats
                        --min_date=2005-01-01
                        --max_date=2006-12-31
                        --window=120
                        --min_feature_perc=0.8
                        --data_file=./data
                        --label_file=./label
                        --rlabel_file=./rlabel
                        --meta_file=./meta
                        --weight_power=2
                        --weight_file=./weight

    For each ticker, gains within specified min/max date are collected, and
    classified into positive/negative according to the thresholds.
    For each dated gain, features are joined by looking back a specified max
    window and using the most recent value (or 0 if not found).

    If --date_file is specified, only dates in the file (and satisfying
    min/max date thresholds) will be selcted for data collection.

    These files are written:
    data_file: matrix of features delimited by space.  Features are in the
               same order as specified by feature_list.
    label_file: list of labels corresponding to each row in data_file.
    rlabel_file: list of regression labels corresponding to each row in data_file.
    meta_file: ticker, gain date and feature count, and actual gain
               corresponding to each row in data_file.
    (optional) weight_file: weight of each data point.
"""

import argparse
import bisect
import datetime
import logging
import numpy
import os
import util

DEBUG = False
MISSING_VALUE = numpy.nan

def readFeatureList(feature_list_file):
  with open(feature_list_file, 'r') as fp:
    return [line for line in fp.read().splitlines()
            if line != '' and not line.startswith('#')]

def readFeatureRanges(feature_stats_file):
  with open(feature_stats_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 0
  assert lines[0] == 'feature\\stats\tcoverage\t1perc\t99perc'
  feature_ranges = dict()
  for i in range(1, len(lines)):
    feature, coverage, perc1, perc99 = lines[i].split('\t')
    perc1 = float(perc1)
    perc99 = float(perc99)
    feature_ranges[feature] = [perc1, perc99]
  return feature_ranges

def collectData(gain_dir, date_file, max_neg, min_pos, feature_base_dir,
                feature_list_file, feature_stats_file, min_date, max_date,
                window, min_feature_perc, data_file, label_file, rlabel_file,
                meta_file, weight_power, weight_file):
  tickers = sorted(os.listdir(gain_dir))
  feature_list = readFeatureList(feature_list_file)
  min_feature_count = int(len(feature_list) * min_feature_perc)
  feature_ranges = readFeatureRanges(feature_stats_file)
  for feature in feature_list:
    if feature not in feature_ranges:
      assert (feature.find('gain') > 0 or
              feature.find('price') > 0 or
              feature.find('volume') > 0 or
              feature.find('volatility') > 0 or
              feature.find('_hp') > 0 or
              feature.startswith('sector') or
              feature.startswith('industry') or
              feature.startswith('window')), (
          'no range info for feature %s' % feature)
      feature_ranges[feature] = [float('-Inf'), float('Inf')]
    lower, upper = feature_ranges[feature]

  data_fp = open(data_file, 'w')
  label_fp = open(label_file, 'w')
  rlabel_fp = open(rlabel_file, 'w')
  meta_fp = open(meta_file, 'w')
  weight_fp = None
  if weight_file:
    weight_fp = open(weight_file, 'w')

  skip_stats = {'feature_file': 0,
                'index': 0,
                'min_date': 0,
                'max_date': 0,
                'filter_date': 0,
                'neg_pos': 0,
                'window': 0,
                'min_perc': 0,
                '1_perc': 0,
                '99_perc': 0}

  dates = None
  if date_file:
    with open(date_file, 'r') as fp:
      dates = set(fp.read().splitlines())

  for ticker in tickers:
    gain_file = '%s/%s' % (gain_dir, ticker)
    gains = util.readKeyValueList(gain_file)

    feature_items = [[] for i in range(len(feature_list))]
    for i in range(len(feature_list)):
      feature_file = '%s/%s/%s' % (feature_base_dir, feature_list[i], ticker)
      if not os.path.isfile(feature_file):
        skip_stats['feature_file'] += 1
        continue
      items = util.readKeyValueList(feature_file)
      for j in range(len(items)):
        if items[j][0] == '*':
          continue
        ymd = items[j][0].split('-')
        if len(ymd) == 3:
          continue
        # Change yyyy-mm to yyyy-mm-01
        assert len(ymd) == 2
        items[j][0] += '-01'
      feature_items[i] = items

    for gain_date, gain in gains:
      if gain_date < min_date:
        skip_stats['min_date'] += 1
        continue
      if gain_date > max_date:
        skip_stats['max_date'] += 1
        continue
      if dates is not None and gain_date not in dates:
        skip_stats['filter_date'] += 1
        continue

      if max_neg < gain and gain < min_pos:
        skip_stats['neg_pos'] += 1
        # Do not skip these they need to be part of testing data.
        # Instead output negative label and postpone filtering to filter_metadata
        # (remove negative labels for training and not for testing).
        #continue

      if DEBUG:
        print 'gain: %f (%s)' % (gain, gain_date)

      if gain <= max_neg:
        weight = max_neg - gain
        label = 0.0
      elif gain >= min_pos:
        weight = gain - min_pos
        label = 1.0
      else:
        weight = 0.0
        label = -1.0
      weight = weight**weight_power

      features = [MISSING_VALUE for i in range(len(feature_list))]
      feature_count = 0
      for i in range(len(feature_list)):
        if len(feature_items[i]) == 1 and feature_items[i][0][0] == '*':
          # undated feature, eg sector
          index = 0
        else:
          # dated feature, eg pgain
          feature_dates = [item[0] for item in feature_items[i]]
          index = bisect.bisect_right(feature_dates, gain_date) - 1
          if index < 0:
            skip_stats['index'] += 1
            continue

          gain_date_obj = datetime.datetime.strptime(gain_date, '%Y-%m-%d')
          feature_date_obj = datetime.datetime.strptime(feature_dates[index],
                                                        '%Y-%m-%d')
          delta = (gain_date_obj - feature_date_obj).days
          if delta > window:
            skip_stats['window'] += 1
            continue

        feature = feature_items[i][index][1]
        lower, upper = feature_ranges[feature_list[i]]
        if feature < lower:
          skip_stats['1_perc'] += 1
          continue
        if feature > upper:
          skip_stats['99_perc'] += 1
          continue

        if DEBUG:
          print 'feature %s: (%s, %f)' % (
              feature_list[i], feature_items[i][index][0], feature)

        features[i] = feature
        feature_count += 1

      if feature_count < min_feature_count:
        skip_stats['min_perc'] += 1
        continue

      print >> data_fp, ' '.join(['%f' % feature for feature in features])
      print >> label_fp, '%f' % label
      print >> rlabel_fp, '%f' % gain
      print >> meta_fp, '%s\t%s\t%d\t%f' % (
          ticker, gain_date, feature_count, gain)
      if weight_fp:
        print >> weight_fp, '%f' % weight

    if DEBUG: break

  data_fp.close()
  label_fp.close()
  rlabel_fp.close()
  meta_fp.close()
  if weight_fp:
    weight_fp.close()
  logging.info('skip_stats: %s' % skip_stats)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--gain_dir', required=True)
  parser.add_argument('--date_file')
  parser.add_argument('--max_neg', type=float, default=0.01)
  parser.add_argument('--min_pos', type=float, default=0.01)
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--feature_list', required=True)
  parser.add_argument('--feature_stats', required=True,
                      help='feature stats file with 1/99 percentiles '
                           'to filter out bad feature values')
  parser.add_argument('--min_date', default='0000-00-00')
  parser.add_argument('--max_date', default='9999-99-99')
  # Most features have a max lag of one quarter.
  parser.add_argument('--window', type=int, default=120)
  parser.add_argument('--min_feature_perc', type=float, default=0.8,
                      help='only use a feature vector if at least certain '
                           'perc of features are populated')
  parser.add_argument('--data_file', required=True)
  parser.add_argument('--label_file', required=True)
  parser.add_argument('--rlabel_file', required=True)
  parser.add_argument('--meta_file', required=True)
  parser.add_argument('--weight_power', type=float, default=1.0)
  parser.add_argument('--weight_file',
                      help='if specified, will assign a weight to each '
                           'training sample with its distance to the '
                           'pos/neg threshold')
  args = parser.parse_args()
  assert args.max_neg <= args.min_pos, 'max_neg > min_pos: %f vs %f' % (
      args.max_neg, args.min_pos)
  util.configLogging()
  collectData(args.gain_dir, args.date_file, args.max_neg, args.min_pos,
              args.feature_base_dir, args.feature_list, args.feature_stats,
              args.min_date, args.max_date, args.window, args.min_feature_perc,
              args.data_file, args.label_file, args.rlabel_file, args.meta_file,
              args.weight_power, args.weight_file)

if __name__ == '__main__':
  main()

