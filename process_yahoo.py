#!/usr/bin/python

""" Samples price, adjprice, vol, vol for first trading day of each month.
    (The last column is supposed to be adjvol, but we don't have that for
    yahoo data so we use vol instead).
    EDIT: actually yahoo may not have unadjusted vol (ie, vol is actually
    adjvol).  We don't rely on (adj)vol much so this is okay for now.
"""

import argparse
import os
import util

EXTENSION = '.csv'
HEADER = 'Date,Open,High,Low,Close,Volume,Adj Close'

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
      for i in range(len(lines) - 1, 0, -1):
        ymd, op, hi, lo, cl, vo, acl = lines[i].split(',')
        if previous_ymd is not None:
          assert ymd > previous_ymd
        previous_ymd = ymd
        ym = util.ymdToYm(ymd)
        if ym == previous_ym:
          continue
        previous_ym = ym
        print >> fp, '%s\t%s\t%s\t%s\t%s' % (
            ymd, cl, acl, vo, vo)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--processed_dir', required=True)
  args = parser.parse_args()
  processYahoo(args.raw_dir, args.processed_dir)

if __name__ == '__main__':
  main()

