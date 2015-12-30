#!/usr/bin/python2.7

""" Computes gains on adjusted opening price for all stocks.

    Example usage:
      ./compute_open_gain.py --yahoo_dir=./yahoo
                             --k=5
                             --gain_dir=./gain/5
                             --fill

    Gain = (adj_open_in_k+1_day - adj_open_in_1_day) / (adj_open_in_1_day + eps)

    If --fill is specified, gains will be computed for all dates up to the last
    trading day for the ticker.  Since the gains are unknown for these dates
    yet, 0 will be written as gains.  This is to facilitate the training /
    prediction process to also handle prediction for the current date.
"""

import argparse
import logging
import os
import util

EPS = 0.01

MIN_GAIN = -1.0
MAX_GAIN = 10.0

def computeOpenGain(args):
  tickers = sorted(os.listdir(args.yahoo_dir))
  stats = {
      'total': 0,
      'nolabel': 0,
      'mincap': 0,
      'maxcap': 0,
  }

  for ticker in tickers:
    dates, opens, closes, adjcloses = util.readYahoo(
        '%s/%s' % (args.yahoo_dir, ticker), 'date,open,close,adjclose')
    with open('%s/%s' % (args.gain_dir, ticker), 'w') as fp:
      for i in range(len(dates)):
        stats['total'] += 1
        p = i + 1  # buy
        q = p + args.k  # sell
        gain = None
        if q >= len(dates):
          stats['nolabel'] += 1
          if not args.fill:
            continue
          else:
            gain = 0.0
        if gain is not None:  # fill
          print >> fp, '%s\t%f' % (dates[i], gain)
          continue
        adjopen1 = opens[p] * adjcloses[p] / closes[p]
        adjopen2 = opens[q] * adjcloses[q] / closes[q]
        gain = (adjopen2 - adjopen1) / (adjopen1 + EPS)
        if gain < MIN_GAIN:
          stats['mincap'] += 1
          gain = MIN_GAIN
        if gain > MAX_GAIN:
          stats['maxcap'] += 1
          gain = MAX_GAIN
        print >> fp, '%s\t%f' % (dates[i], gain)
  logging.info('output: stats: %s' % stats)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--yahoo_dir', required=True)
  parser.add_argument('--k', type=int, required=True,
                      help='number of days to look for gain')
  parser.add_argument('--fill', action='store_true')
  parser.add_argument('--gain_dir', required=True)
  args = parser.parse_args()
  util.configLogging()
  computeOpenGain(args)

if __name__ == '__main__':
  main()

