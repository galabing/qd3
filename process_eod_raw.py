#!/usr/bin/python

""" Samples price, adjprice, vol, adjvol for first trading day of each month.
"""

import argparse
import os
import util

def processEodRaw(raw_dir, ticker_file, processed_dir):
  tickers = util.readTickers(ticker_file)
  for ticker in tickers:
    raw_file = '%s/%s' % (raw_dir, ticker)
    if not os.path.isfile(raw_file):
      continue
    with open(raw_file, 'r') as fp:
      lines = fp.read().splitlines()
    processed_file = '%s/%s' % (processed_dir, ticker)
    with open(processed_file, 'w') as fp:
      previous_ymd = None
      previous_ym = None
      for line in lines:
        _, ymd, op, hi, lo, cl, vo, di, sp, aop, ahi, alo, acl, avo = (
            line.split(','))
        assert _ == ticker
        if previous_ymd is not None:
          assert ymd > previous_ymd
        previous_ymd = ymd
        ym = util.ymdToYm(ymd)
        if ym == previous_ym:
          continue
        previous_ym = ym
        print >> fp, '%s\t%s\t%s\t%s\t%s' % (
            ymd, cl, acl, vo, avo)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--processed_dir', required=True)
  args = parser.parse_args()
  processEodRaw(args.raw_dir, args.ticker_file, args.processed_dir)

if __name__ == '__main__':
  main()

