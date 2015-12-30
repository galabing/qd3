#!/usr/bin/python2.7

""" Projects yahoo data by trading days into:
        yyyy-mm-dd open high low close adj_close volume
    separated by tabs, with all dates being trading days
    and sorted in ascending order.

    Example usage:
      ./project_yahoo.py --raw_dir=./raw
                         --trading_day_file=./trading_days
                         --projected_dir=./projected
"""

import argparse
import os

def projectYahoo(args):
  tickers = sorted([f[:f.rfind('.')] for f in os.listdir(args.raw_dir)
                    if f.endswith('.csv')])
  with open(args.trading_day_file, 'r') as fp:
    trading_days = fp.read().splitlines()
  trading_days.sort()
  for ticker in tickers:
    with open('%s/%s.csv' % (args.raw_dir, ticker), 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
    data = dict()  # date => [open, high, low, close, adj_close, volume]
    for i in range(1, len(lines)):
      date, op, hi, lo, cl, vo, adjcl = lines[i].split(',')
      assert date not in data
      data[date] = [op, hi, lo, cl, adjcl, vo]
    with open('%s/%s' % (args.projected_dir, ticker), 'w') as fp:
      for date in trading_days:
        if date not in data:
          continue
        print >> fp, '%s\t%s' % (date, '\t'.join(data[date]))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--trading_day_file', required=True)
  parser.add_argument('--projected_dir', required=True)
  projectYahoo(parser.parse_args())

if __name__ == '__main__':
  main()

