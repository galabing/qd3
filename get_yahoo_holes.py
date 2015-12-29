#!/usr/bin/python2.7

""" Example usage:
      ./get_yahoo_holes.py --raw_dir=./raw
                           --trading_day_file=./trading_days
                           --window=252
                           --output_dir=./holes
"""

from collections import deque
import argparse
import bisect
import os

def getHoles(args):
  tickers = sorted([f[:f.rfind('.')] for f in os.listdir(args.raw_dir)
                    if f.endswith('.csv')])
  with open(args.trading_day_file, 'r') as fp:
    trading_days = fp.read().splitlines()

  for i in range(len(trading_days) - 1):
    assert trading_days[i+1] > trading_days[i]  # ascending

  for ticker in tickers:
    with open('%s/%s.csv' % (args.raw_dir, ticker), 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
    dates = []
    for i in range(1, len(lines)):
      date = lines[i][:lines[i].find(',')]
      if len(dates) == 0:
        dates.append(date)
      else:
        assert date < dates[-1]
        dates.append(date)
    min_date = dates[-1]
    dates = set(dates)

    with open('%s/%s' % (args.output_dir, ticker), 'w') as fp:
      # For each trading day (after the first day of the ticker),
      # count the number of holes in the past [window] trading days
      # and output count/window ratio.
      index = bisect.bisect_left(trading_days, min_date)
      buffer = deque(maxlen=args.window)
      while index < len(trading_days):
        date = trading_days[index]
        if date in dates:
          buffer.append(1)
        else:
          buffer.append(0)
        print >> fp, '%s\t%f' % (date, float(buffer.count(0))/len(buffer))
        index += 1

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--trading_day_file', required=True)
  parser.add_argument('--window', type=int, default=252)
  parser.add_argument('--output_dir', required=True)
  getHoles(parser.parse_args())

if __name__ == '__main__':
  main()

