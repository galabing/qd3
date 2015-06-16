#!/usr/bin/python

# Adapted from qd.
""" Computes log of any basic feature from any dimension file.

    Example usage:
      ./compute_log_feature.py --processed_dir=./processed
                               --ticker_file=./tickers
                               --dimension=ARQ
                               --header=CAPEX
                               --negate
                               --feature_dir=./CAPEX-ARQ
                               --info_file=./CAPEX-ARQ/info
"""

import argparse
import math
import util

def computeLogFeature(processed_dir, ticker_file, dimension, header,
                      negate, feature_dir, info_file=None):
  tickers = util.readTickers(ticker_file)
  feature_info = []
  for ticker in tickers:
    dimension_file = '%s/%s/%s.tsv' % (processed_dir, ticker, dimension)
    dfeatures = util.readSf1Column(dimension_file, header)
    if dfeatures is None:
      continue
    with open('%s/%s' % (feature_dir, ticker), 'w') as fp:
      for date, feature in dfeatures:
        year = util.ymdToY(date)
        if feature is None:
          feature_info.append((year, None))
          continue
        if negate:
          feature = -feature
        if feature <= 0:
          feature_info.append((year, None))
          continue
        feature = math.log(feature)
        print >> fp, '%s\t%f' % (date, feature)
        feature_info.append((year, feature))
  if info_file is not None:
    util.writeFeatureInfo(
        [processed_dir, ticker_file, dimension, header, negate, feature_dir],
        feature_info, info_file)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--processed_dir', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--dimension', required=True)
  parser.add_argument('--header', required=True)
  parser.add_argument('--negate', action='store_true',
                      help='negate the feature (eg, CAPEX)')
  parser.add_argument('--feature_dir', required=True)
  parser.add_argument('--info_file')
  args = parser.parse_args()
  computeLogFeature(args.processed_dir, args.ticker_file, args.dimension,
                    args.header, args.negate, args.feature_dir,
                    args.info_file)

if __name__ == '__main__':
  main()

