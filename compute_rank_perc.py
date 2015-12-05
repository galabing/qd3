#!/usr/bin/python2.7

""" Ranks values for each date and computes percentile for each ticker.

    Example usage:
      ./compute_rank_perc.py
          --input_dir=./volatility
          --output_dir=./volatility_perc
"""

import argparse
import os
import util

def computePerc(input_dir, output_dir):
  tickers = sorted(os.listdir(input_dir))
  dvalues = dict()  # date => [[ticker, value] ...]
  for ticker in tickers:
    data = util.readKeyValueList('%s/%s' % (input_dir, ticker))
    for date, value in data:
      if date not in dvalues:
        dvalues[date] = [[ticker, value]]
      else:
        dvalues[date].append([ticker, value])
  # Convert raw value to perc.
  for tvalues in dvalues.itervalues():
    tvalues.sort(key=lambda item: item[1])
    for i in range(len(tvalues)):
      tvalues[i][1] = float(i)/len(tvalues)
  tvalues = dict()  # ticker => [[date, perc] ...]
  for date, tpercs in dvalues.iteritems():
    for ticker, perc in tpercs:
      if ticker not in tvalues:
        tvalues[ticker] = [[date, perc]]
      else:
        tvalues[ticker].append([date, perc])
  # Write output.
  for ticker, values in tvalues.iteritems():
    values.sort(key=lambda value: value[0])
    with open('%s/%s' % (output_dir, ticker), 'w') as fp:
      for date, perc in values:
        print >> fp, '%s\t%f' % (date, perc)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  computePerc(args.input_dir, args.output_dir)

if __name__ == '__main__':
  main()

