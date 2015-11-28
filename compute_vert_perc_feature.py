#!/usr/bin/python2.7

""" Computes vertical percentile features.

    Example usage:
      ./compute_vert_perc_feature.py --input_dir=./features
                                     --output_dir=./features
                                     --feature=TAXRATE-ART
                                     --windows=0,1,2,3,4,8,16
                                     --ticker_file=./tickers
                                     --info_base_dir=./info

      ./compute_vert_perc_feature.py --input_dir=./yahoo
                                     --output_dir=./features
                                     --feature=adjprice
                                     --windows=0,1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48
                                     --ticker_file=./tickers
                                     --info_base_dir=./info
"""

import argparse
import logging
import os
import util

def getTarget(feature, window):
  return '%s_hp-%d' % (feature, window)

def getTargetDir(feature_dir, feature, window):
  return '%s/%s' % (feature_dir, getTarget(feature, window))

def collectData(data, index, windows):
  date = data[index][0]
  ws, vs = [], []
  for window in windows:
    i = index - window
    if i < 0:
      continue
    ws.append(window)
    vs.append(data[i][1])
  return date, ws, vs

def computePerc(vs):
  ps = [0.5 for v in vs]  # Use 0.5 as default percentile.
  maxv, minv = max(vs), min(vs)
  span = maxv - minv
  if span < 1e-5:
    return ps
  for i in range(len(vs)):
    ps[i] = (vs[i] - minv) / span
  return ps

def computeVertPercFeature(input_dir, output_dir, feature, windows_str, ticker_file, info_dir):
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
      date, ws, vs = collectData(data, index, windows)
      ps = computePerc(vs)
      for i in range(len(ws)):
        print >> ofps[ws[i]], '%s\t%f' % (date, ps[i])
      year = util.ymdToY(date)
      for window in windows:
        try:
          i = ws.index(window)
          feature_info[window].append((year, ps[i]))
        except ValueError:
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
  computeVertPercFeature(args.input_dir, args.output_dir, args.feature,
                         args.windows, args.ticker_file, args.info_base_dir)

if __name__ == '__main__':
  main()

