#!/usr/bin/python

# Adapted from qd.
""" Collects price or volume data.  Each input file should have five columns:
    date, price, adj price, volume, adj volume.

    Example usage:
      ./get_price_volume.py --processed_dir=./processed
                            --column=price  # or adjprice, volume, adjvolume
                            --take_log
                            --output_dir=./logprices
"""

import argparse
import math
import os
import util

# column => index
INDEX = {
  'price': 1,
  'adjprice': 2,
  'volume': 3,
  'adjvolume': 4,
}

def getData(processed_dir, column, take_log, output_dir):
  tickers = sorted(os.listdir(processed_dir))
  index = INDEX[column]
  for ticker in tickers:
    with open('%s/%s' % (processed_dir, ticker), 'r') as fp:
      lines = fp.read().splitlines()
    with open('%s/%s' % (output_dir, ticker), 'w') as fp:
      for line in lines:
        items = line.split('\t')
        date = items[0]
        data = items[index]
        if date == '' or data == '':
          continue
        data = float(data)
        if data <= 0:
          continue
        if take_log:
          data = math.log(data)
        print >> fp, '%s\t%f' % (date, data)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--processed_dir', required=True)
  parser.add_argument('--column', required=True,
                      choices=['price', 'adjprice', 'volume', 'adjvolume'])
  parser.add_argument('--take_log', action='store_true',
                      help='take log of price/volume')
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  getData(args.processed_dir, args.column, args.take_log, args.output_dir)

if __name__ == '__main__':
  main()

