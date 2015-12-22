#!/usr/bin/python2.7

""" Computes vertical gain features.

    Example usage:
      ./compute_vert_gain_feature.py --input_dir=./features
                                     --output_dir=./features
                                     --feature=TAXRATE-ART
                                     --windows=4,8,16
                                     --ticker_file=./tickers
                                     --info_base_dir=./info
"""

import argparse
import logging
import os
import util

EPS = 1e-5

def getTarget(feature, window):
  return '%s_vg-%d' % (feature, window)

def getTargetDir(feature_dir, feature, window):
  return '%s/%s' % (feature_dir, getTarget(feature, window))

def compute(data, index, windows):
  date, newv = data[index]
  gains = dict()
  for window in windows:
    if index - window < 0:
      continue
    oldv = data[index - window][1]
    if abs(oldv) < EPS:
      continue
    gains[window] = (newv - oldv) / oldv
  return date, gains

def computeVertGainFeature(input_dir, output_dir, feature, windows_str, ticker_file, info_dir):
  windows = [int(w) for w in windows_str.split(',')]
  tickers = util.readTickers(ticker_file)
  feature_info = {w: [] for w in windows}  # [[yyyy, feature] ...]

  for window in windows:
    target_dir = getTargetDir(output_dir, feature, window)
    if not os.path.isdir(target_dir):
      os.mkdir(target_dir)

  for ticker in tickers:
    feature_file = '%s/%s/%s' % (input_dir, feature, ticker)
    if not os.path.isfile(feature_file):
      continue
    data = util.readKeyValueList(feature_file)

    ofps = {w: open('%s/%s' % (getTargetDir(output_dir, feature, w), ticker), 'w')
            for w in windows}

    for index in range(len(data)):
      date, gains = compute(data, index, windows)
      year = util.ymdToY(date)
      for window, gain in gains.iteritems():
        print >> ofps[window], '%s\t%f' % (date, gain)
      for window in windows:
        if window in gains:
          feature_info[window].append((year, gains[window]))
        else:
          feature_info[window].append((year, None))

    for ofp in ofps.itervalues():
      ofp.close()

  for window in windows:
    target = getTarget(feature, window)
    util.writeFeatureInfo(
        [input_dir, output_dir, feature, windows_str, ticker_file],
        feature_info[window], '%s/%s' % (info_dir, target))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--feature', required=True)
  parser.add_argument('--windows', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--info_base_dir', required=True)
  args = parser.parse_args()
  computeVertGainFeature(args.input_dir, args.output_dir, args.feature,
                         args.windows, args.ticker_file, args.info_base_dir)

if __name__ == '__main__':
  main()

