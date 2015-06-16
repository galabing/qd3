#!/usr/bin/python

# Adapted from qd.
""" Computes excess gains.

    Example usage:
      ./compute_egain.py --gain_dir=./gain/6
                         --market_file=./sp500/6
                         --egain_dir=./egain/6
"""

import argparse
import logging
import os
import util

# ym => [ymd, gain]
def getGainDict(gain_file):
  dgains = util.readKeyValueList(gain_file)
  gain_dict = dict()
  for date, gain in dgains:
    ym = util.ymdToYm(date)
    assert ym not in gain_dict
    gain_dict[ym] = [date, gain]
  return gain_dict

def computeEgain(gain_dir, market_file, egain_dir):
  tickers = sorted(os.listdir(gain_dir))
  market_dict = getGainDict(market_file)

  missing = 0
  for ticker in tickers:
    gain_file = '%s/%s' % (gain_dir, ticker)
    ticker_dict = getGainDict(gain_file)
    with open('%s/%s' % (egain_dir, ticker), 'w') as fp:
      for ym in sorted(ticker_dict.keys()):
        if ym in market_dict:
          date, ticker_gain = ticker_dict[ym]
          tmp, market_gain = market_dict[ym]
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

