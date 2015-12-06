#!/usr/bin/python2.7

""" Computes horizontal percentile feature.

    Example usage:
      ./compute_hori_perc_feature.py --input_dir=./PE-ART
                                     --group_map_file=./sector_map
                                     --output_dir=./PE-ART_hp
                                     --rank

    For each ticker on each date, tickers within the same group as specified
    in --group_map_file (or all tickers if this is not set) are collected and
    percentile for this ticker is calculated.

    There are two ways of calculating percentile:
      1. using 0-based-rank divided by total count if --rank is set
      2. using (val - min) / (max - min) if --rank is not set

    Dates are aligned when calculating percentile. Eg, when processing AAPL on
    2010-01-23, the most recent numbers from other tickers on or before
    2010-01-23 are collected for calculation.

    --group_map_file, if specified, is assumed to contain mapping between
    ticker and group names, eg: <ticker>\t<sector>.
"""

import argparse
import bisect
import os
import util

EPS = 1e-5

def readGroupMap(group_map_file):
  with open(group_map_file, 'r') as fp:
    lines = fp.read().splitlines()
  groups = dict()  # ticker => group
  for line in lines:
    ticker, group = line.split('\t')
    groups[ticker] = group
  return groups

def computePerc(value, others, rank):
  values = [value] + others
  if not rank:
    maxv = max(values)
    minv = min(values)
    span = maxv - minv
    if span < EPS:
      return 0.5
    else:
      return (value - minv) / span
  if len(values) == 1:
    return 0.5
  values.sort()
  index = bisect.bisect_right(values, value) - 1
  assert index >= 0
  return float(index)/len(values)

def computePercFeature(args):
  tickers = sorted(os.listdir(args.input_dir))
  group_map = None
  if args.group_map_file:
    group_map = readGroupMap(args.group_map_file)
  ticker_map = None  # inverse of group_map, group => tickers
  if group_map is not None:
    ticker_map = dict()
    for ticker, group in group_map.iteritems():
      if group not in ticker_map:
        ticker_map[group] = [ticker]
      else:
        ticker_map[group].append(ticker)

  # ticker => [dates, values]
  data = dict()
  for ticker in tickers:
    dates, values = [], []
    prev_date = None
    for date, value in util.readKeyValueList('%s/%s' % (args.input_dir, ticker)):
      if prev_date is None:
        prev_date = date
      else:
        assert date > prev_date
      dates.append(date)
      values.append(value)
    data[ticker] = [dates, values]

  for ticker in tickers:
    if group_map is None:
      group = tickers
    else:
      group = ticker_map[group_map[ticker]]
    dates, values = data[ticker]
    with open('%s/%s' % (args.output_dir, ticker), 'w') as fp:
      for i in range(len(dates)):
        others = []
        for other in group:
          if other == ticker:
            continue
          odates, ovalues = data[other]
          index = bisect.bisect_right(odates, dates[i]) - 1
          if index >= 0:
            others.append(ovalues[index])
        print >> fp, '%s\t%f' % (dates[i], computePerc(values[i], others, args.rank))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--group_map_file')
  parser.add_argument('--rank', action='store_true')
  parser.add_argument('--output_dir', required=True)
  computePercFeature(parser.parse_args())

if __name__ == '__main__':
  main()

