#!/usr/bin/python2.7

# Adapted from qd.
""" Computes excess gains.

    Example usage:
      ./compute_egain_2.py --gain_dir=./gain/5
                           --market_file=./sp500/5
                           --egain_dir=./egain/5
"""

import argparse
import logging
import os
import util

def computeEgain(gain_dir, market_file, egain_dir):
  tickers = sorted(os.listdir(gain_dir))
  market_dict = util.readKeyValueDict(market_file)

  missing = 0
  for ticker in tickers:
    gain_file = '%s/%s' % (gain_dir, ticker)
    ticker_dict = util.readKeyValueDict(gain_file)
    with open('%s/%s' % (egain_dir, ticker), 'w') as fp:
      for date in sorted(ticker_dict.keys()):
        if date in market_dict:
          ticker_gain = ticker_dict[date]
          market_gain = market_dict[date]
          print >> fp, '%s\t%f' % (date, ticker_gain - market_gain)
        else:
          missing += 1
  logging.info('%d missing dates from market' % missing)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--gain_dir', required=True)
  parser.add_argument('--market_file', required=True)
  parser.add_argument('--egain_dir', required=True)
  args = parser.parse_args()
  util.configLogging()
  computeEgain(args.gain_dir, args.market_file, args.egain_dir)

if __name__ == '__main__':
  main()

