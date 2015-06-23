#!/usr/bin/python2.7

""" Samples price, adjprice, vol, vol for first trading day of each month.
    (The last column is supposed to be adjvol, but we don't have that for
    yahoo data so we use vol instead).
    EDIT: actually yahoo may not have unadjusted vol (ie, vol is actually
    adjvol).  We don't rely on (adj)vol much so this is okay for now.

    For price and adjprice, it's just the closing value of the day.
    For vol and adjvol, it's the average value across the previous month.
"""

import argparse
import os
import util

EXTENSION = '.csv'
HEADER = 'Date,Open,High,Low,Close,Volume,Adj Close'

def getVolume(v):
  if v == '': return 0.0
  return float(v)

def processYahoo(raw_dir, processed_dir):
  raw_files = os.listdir(raw_dir)
  for raw_file in raw_files:
    assert raw_file.endswith(EXTENSION)
    ticker = raw_file[:-len(EXTENSION)]
    input_file = '%s/%s' % (raw_dir, raw_file)
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == HEADER
    processed_file = '%s/%s' % (processed_dir, ticker)
    with open(processed_file, 'w') as fp:
      previous_ymd = None
      previous_ym = None
      previous_vo = 0.0
      previous_days = 0
      for i in range(len(lines) - 1, 0, -1):
        ymd, op, hi, lo, cl, vo, acl = lines[i].split(',')
        if previous_ymd is not None:
          assert ymd > previous_ymd
        previous_ymd = ymd
        ym = util.ymdToYm(ymd)
        if ym != previous_ym:
          previous_ym = ym
          if previous_days > 0:
            previous_vo /= previous_days
          print >> fp, '%s\t%s\t%s\t%s\t%s' % (
              ymd, cl, acl, previous_vo, previous_vo)
          previous_vo = 0.0
          previous_days = 0
        previous_vo += getVolume(vo)
        previous_days += 1

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--processed_dir', required=True)
  args = parser.parse_args()
  processYahoo(args.raw_dir, args.processed_dir)

if __name__ == '__main__':
  main()

