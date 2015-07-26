#!/usr/bin/python2.7

""" Filters training/prediction metadata by:
    - raw price
    - membership
    etc.

    Example usage:
      ./filter_metadata.py --input_file=./meta
                           --min_raw_price=10
                           --raw_price_dir=./price
                           --membership_file=./membership
                           --output_file=./filtered_meta

    Only metadata (ticker-date pairs) that pass through all filters
    are kept in output.

    --min_raw_price: only keep tickers that are trading above this
                     price on the trading day (requires --raw_price_dir).
    --membership_file: only keep tickers that are part of some membership
                       on the trading day.
    Both flags are optional.  If not set, the corresponding filter will
    be disabled.  If none is set, --output_file should contain identical
    content to --input_file.
"""

import argparse
import logging

MIN_RAW_PRICE = float('-Inf')

def readMembership(membership_file):
  with open(membership_file, 'r') as fp:
    lines = fp.read().splitlines()
  membership = dict()
  for line in lines:
    ticker, periods = line.split('\t')
    periods = periods.split(' ')
    assert ticker not in membership
    value = []  # [[start, end] ...]
    for period in periods:
      start, end = period.split(',')
      assert start < end
      if len(value) > 0:
        assert start >= value[-1][1]
      value.append([start, end])
    membership[ticker] = value
  return membership

def readPrice(price_file):
  with open(price_file, 'r') as fp:
    lines = fp.read().splitlines()
  price = dict()
  for line in lines:
    date, value = line.split('\t')
    assert date not in price
    price[date] = float(value)
  return price

def isMember(membership, ticker, date):
  if ticker not in membership:
    return False
  periods = membership[ticker]
  for start, end in periods:
    if date >= start and date < end:
      return True
  return False

def filterMetadata(input_file, min_raw_price, raw_price_dir,
                   membership_file, output_file):
  stats = {
    'min_raw_price': 0,
    'membership': 0,
  }

  ifp = open(input_file, 'r')
  ofp = open(output_file, 'w')
  prev_ticker = None
  price = None  # for prev_ticker, date => price
  if membership_file is None:
    membership = None
  else:
    membership = readMembership(membership_file)  # ticker => [[start, end] ...]
  while True:
    line = ifp.readline()
    if line == '':
      break
    assert line.endswith('\n')
    items = line[:-1].split('\t')
    assert len(items) >= 2
    ticker, date = items[0], items[1]
    if ticker != prev_ticker:
      prev_ticker = ticker
      if raw_price_dir is not None:
        price = readPrice('%s/%s' % (raw_price_dir, ticker))
    # Maybe check price.
    if price is not None:
      assert date in price, 'missing date %s for %s' % (date, ticker)
      if price[date] < min_raw_price:
        stats['min_raw_price'] += 1
        continue
    # Maybe check membership.
    if membership is not None:
      if not isMember(membership, ticker, date):
        stats['membership'] += 1
        continue
    print >> ofp, line[:-1]
  logging.info('skip_stats: %s' % stats)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', required=True)
  parser.add_argument('--min_raw_price', type=float, default=MIN_RAW_PRICE)
  parser.add_argument('--raw_price_dir')
  parser.add_argument('--membership_file')
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()
  if args.min_raw_price > MIN_RAW_PRICE:
    assert args.raw_price_dir is not None, (
        'must also specify --raw_price_dir since --min_raw_price is specified')
  else:
    assert args.raw_price_dir is None
  filterMetadata(args.input_file, args.min_raw_price, args.raw_price_dir,
                 args.membership_file, args.output_file)

if __name__ == '__main__':
  main()

