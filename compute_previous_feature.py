#!/usr/bin/python2.7

# Adapted from qd.
""" Computes previous features.  This simply takes dated features and reindex
    them by the end date so that it can be used as a feature.  Eg, in a
    6-month gain file, a row could be:
      2000-01-01 0.1
    meaning the gain 6 months from 2000-01-01 is 10%.  This will be converted
    to:
      2000-07-01 0.1
    meaning the past 6-month gain ending on 2000-07-01 is 10%.

    Example usage:
      ./compute_previou_feature.py --feature_dir=./gains/6
                                   --k=6
                                   --pfeature_dir=./pgain/6
"""

import argparse
import os
import util

def computePreviousFeature(feature_dir, k, pfeature_dir):
  tickers = sorted(os.listdir(feature_dir))
  for ticker in tickers:
    feature_file = '%s/%s' % (feature_dir, ticker)
    dfeatures = util.readKeyValueList(feature_file)
    with open('%s/%s' % (pfeature_dir, ticker), 'w') as fp:
      for date, feature in dfeatures:
        ym = util.ymdToYm(date)
        pdate = util.getNextYm(ym, k)
        print >> fp, '%s-01\t%f' % (pdate, feature)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--feature_dir', required=True)
  parser.add_argument('--k', type=int,
                      help='number of months in computing feature')
  parser.add_argument('--pfeature_dir', required=True)
  args = parser.parse_args()
  computePreviousFeature(args.feature_dir, args.k, args.pfeature_dir)

if __name__ == '__main__':
  main()

