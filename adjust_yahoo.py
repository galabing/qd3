#!/usr/bin/python2.7

""" Adjusts yahoo price data.

    Example usage:
      ./adjust_yahoo.py --yahoo_dir=./yahoo
                        --output_dir=./adjusted
"""

import argparse
import os
import util

def adjust(raw, ratios):
  for i in range(len(raw)):
    raw[i] *= adjcloses[i] / closes[i]

def output(base_dir, label, ticker, dates, values):
  output_dir = '%s/%s' % (base_dir, label)
  if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
  with open('%s/%s' % (output_dir, ticker), 'w') as fp:
    for i in range(len(dates)):
      print >> fp, '%s\t%f' % (dates[i], values[i])

def adjustYahoo(args):
  tickers = sorted(os.listdir(args.yahoo_dir))
  for ticker in tickers:
    dates, opens, highs, lows, closes, adjcloses, volumes = util.readYahoo(
        '%s/%s' % (args.yahoo_dir, ticker), 'date,open,high,low,close,adjclose,volume')
    ratios = [adjcloses[i]/closes[i] for i in range(len(dates))]
    adjopens = [opens[i]*ratios[i] for i in range(len(dates))]
    adjhighs = [highs[i]*ratios[i] for i in range(len(dates))]
    adjlows = [lows[i]*ratios[i] for i in range(len(dates))]
    output(args.output_dir, 'open', ticker, dates, adjopens)
    output(args.output_dir, 'high', ticker, dates, adjhighs)
    output(args.output_dir, 'low', ticker, dates, adjlows)
    output(args.output_dir, 'close', ticker, dates, adjcloses)
    output(args.output_dir, 'volume', ticker, dates, volumes)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--yahoo_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  adjustYahoo(parser.parse_args())

if __name__ == '__main__':
  main()

