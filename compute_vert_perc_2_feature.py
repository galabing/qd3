#!/usr/bin/python2.7

""" Computes vertical percentile features.
    Comparison with compute_vert_perc_feature.py:
      Given values [10, 20, 30, 40, 50, 60] and windows 1, 3; at value 60:
      - compute_vert_perc_feature will get values with offset 1 and 3
        (50 and 30) and compute relative percentile among these values
        (1.0 and 0.0) and write them as two features for window 1 and 3
        respectively.
      - compute_vert_perc_2_feature will get all values within the two windows
        ([50, 60] and [30, 40, 50, 60]) and compute percentile of current value
        (60) in each window (1.0 and 1.0) and write them as two features for
        window 1 and 3 respectively.

    Example usage:
      ./compute_vert_perc_2_feature.py --input_dir=./features
                                     --output_dir=./features
                                     --feature=TAXRATE-ART
                                     --windows=4,8,16
                                     --ticker_file=./tickers
                                     --info_base_dir=./info

      ./compute_vert_perc_2_feature.py --input_dir=./yahoo
                                     --output_dir=./features
                                     --feature=adjprice
                                     --windows=3,6,12,24,48
                                     --ticker_file=./tickers
                                     --info_base_dir=./info
"""

import argparse
import logging
import os
import util

def getTarget(feature, window):
  return '%s_vp2-%d' % (feature, window)

def getTargetDir(feature_dir, feature, window):
  return '%s/%s' % (feature_dir, getTarget(feature, window))

def compute(data, index, windows):
  date = data[index][0]
  percs = dict()
  for window in windows:
    values = [data[i][1] for i in range(max(0,index-window), index+1)]
    maxv, minv = max(values), min(values)
    span = maxv - minv
    if span < 1e-5:
      percs[window] = 0.5
    else:
      percs[window] = (values[-1] - minv) / span
  return date, percs

def computeVertPerc2Feature(input_dir, output_dir, feature, windows_str, ticker_file, info_dir):
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
      date, percs = compute(data, index, windows)
      for window, perc in percs.iteritems():
        print >> ofps[window], '%s\t%f' % (date, perc)
      year = util.ymdToY(date)
      for window in windows:
        feature_info[window].append((year, percs[window]))

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
  computeVertPerc2Feature(args.input_dir, args.output_dir, args.feature,
                          args.windows, args.ticker_file, args.info_base_dir)

if __name__ == '__main__':
  main()

