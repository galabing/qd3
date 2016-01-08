#!/usr/bin/python2.7

""" Filters training/prediction metadata by:
    - raw price
    - membership
    etc.

    Example usage:
      ./filter_metadata.py --input_file=./meta
                           --min_raw_price=10
                           --raw_price_dir=./price
                           --max_volatility=0.5
                           --volatility_dir=./volatility_perc
                           --min_volumed=0.5
                           --volumed_dir=./volumed_perc
                           --min_marketcap=2000000000
                           --marketcap_dir=./MARKETCAP-ND
                           --max_holes=0.01
                           --hole_dir=./holes
                           --membership_file=./membership
                           --remove_neg_labels
                           --output_file=./filtered_meta

    Only metadata (ticker-date pairs) that pass through all filters
    are kept in output.

    --min_raw_price: only keep tickers that are trading above this
                     price on the trading day (requires --raw_price_dir).
    --max_volatility: only keep tickers that with less volatility than the
                      threshold (requires --volatility_dir).
    --min_volumed: only keep tickers that are trading above certain volume
                   (requires --volumed_dir).
    --min_marketcap: only keep tickers with larger market cap than the
                     threshold (requires --marketcap_dir).
    --max_holes: only keep tickers with less holes than the threshold
                 (requires --hole_dir).
    --membership_file: only keep tickers that are part of some membership
                       on the trading day.
    --remove_neg_labels: only keep zero and positive labels (for training).
    For testing all labels should be kept, including the ones assigned with
    negative labels (ie, gain is between max_neg and min_pos).

    All flags are optional.  If not set, the corresponding filter will
    be disabled.  If none is set, --output_file should contain identical
    content to --input_file.
"""

import argparse
import bisect
import logging
import util

MIN_RAW_PRICE = float('-Inf')
MAX_VOLATILITY = float('Inf')
MIN_VOLUMED = float('-Inf')
MIN_MARKETCAP = float('-Inf')
MAX_HOLES = float('Inf')

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
      if period == '':
        continue
      start, end = period.split(',')
      assert start < end
      if len(value) > 0:
        assert start >= value[-1][1]
      value.append([start, end])
    membership[ticker] = value
  return membership

def isMember(membership, ticker, date):
  if ticker not in membership:
    return False
  periods = membership[ticker]
  for start, end in periods:
    if date >= start and date < end:
      return True
  return False

def filterMetadata(input_file, min_raw_price, raw_price_dir,
                   max_volatility, volatility_dir,
                   min_volumed, volumed_dir, min_marketcap,
                   marketcap_dir, max_holes, hole_dir,
                   membership_file, remove_neg_labels,
                   label_file, output_file):
  stats = {
    'min_raw_price': 0,
    'max_volatility': 0,
    'min_volumed': 0,
    'min_marketcap': 0,
    'max_holes': 0,
    'membership': 0,
    'neg_label': 0,
  }

  ifp = open(input_file, 'r')
  if remove_neg_labels:
    lfp = open(label_file, 'r')
  ofp = open(output_file, 'w')

  prev_ticker = None
  price = None  # for prev_ticker, date => price
  volatility = None  # for prev ticker, date => volatility
  volumed = None  # for prev ticker, date => volumed
  marketcap = None  # for prev ticker, [dates, values]
  hole = None  # for prev ticker, [dates, holes]
  if membership_file is None:
    membership = None
  else:
    membership = readMembership(membership_file)  # ticker => [[start, end] ...]

  while True:
    line = ifp.readline()
    if remove_neg_labels:
      lline = lfp.readline()
    if line == '':
      if remove_neg_labels:
        assert lline == '', 'inconsisten line count between meta and label files'
      break
    assert line.endswith('\n')
    items = line[:-1].split('\t')
    assert len(items) >= 2
    ticker, date = items[0], items[1]
    if ticker != prev_ticker:
      prev_ticker = ticker
      if raw_price_dir is not None:
        price = util.readKeyValueDict('%s/%s' % (raw_price_dir, ticker))
      if volatility_dir is not None:
        volatility = util.readKeyValueDict('%s/%s' % (volatility_dir, ticker))
      if volumed_dir is not None:
        volumed = util.readKeyValueDict('%s/%s' % (volumed_dir, ticker))
      if marketcap_dir is not None:
        tmp = util.readKeyValueList('%s/%s' % (marketcap_dir, ticker))
        marketcap_dates = [t[0] for t in tmp]
        marketcap_values = [t[1] for t in tmp]
        marketcap = (marketcap_dates, marketcap_values)
      if hole_dir is not None:
        tmp = util.readKeyValueList('%s/%s' % (hole_dir, ticker))
        hole_dates = [t[0] for t in tmp]
        hole_values = [t[1] for t in tmp]
        hole = (hole_dates, hole_values)
    # Maybe check price.
    if price is not None:
      #assert date in price, 'missing price for %s on %s' % (ticker, date)
      if date not in price or price[date] < min_raw_price:
        stats['min_raw_price'] += 1
        continue
    # Maybe check volatility.
    if volatility is not None:
      #assert date in volatility, 'missing volatility for %s on %s' % (ticker, date)
      if date not in volatility or volatility[date] > max_volatility:
        stats['max_volatility'] += 1
        continue
    if volumed is not None:
      if date not in volumed or volumed[date] < min_volumed:
        stats['min_volumed'] += 1
        continue
    # Maybe check marketcap.
    if marketcap is not None:
      marketcap_dates, marketcap_values = marketcap
      index = bisect.bisect_right(marketcap_dates, date) - 1
      if index < 0 or marketcap_values[index] < min_marketcap:
        stats['min_marketcap'] += 1
        continue
    # Maybe check holes.
    if hole is not None:
      hole_dates, hole_values = hole
      index = bisect.bisect_right(hole_dates, date) - 1
      if index < 0 or hole_values[index] > max_holes:
        stats['max_holes'] += 1
        continue
    # Maybe check membership.
    if membership is not None:
      if not isMember(membership, ticker, date):
        stats['membership'] += 1
        continue
    # Maybe check label.
    if remove_neg_labels:
      assert lline.endswith('\n')
      label = float(lline[:-1])
      if label < 0:
        stats['neg_label'] += 1
        continue
    print >> ofp, line[:-1]
  logging.info('skip_stats: %s' % stats)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', required=True)
  parser.add_argument('--min_raw_price', type=float, default=MIN_RAW_PRICE)
  parser.add_argument('--raw_price_dir')
  parser.add_argument('--max_volatility', type=float, default=MAX_VOLATILITY)
  parser.add_argument('--volatility_dir')
  parser.add_argument('--min_volumed', type=float, default=MIN_VOLUMED)
  parser.add_argument('--volumed_dir')
  parser.add_argument('--min_marketcap', type=float, default=MIN_MARKETCAP)
  parser.add_argument('--marketcap_dir')
  parser.add_argument('--max_holes', type=float, default=MAX_HOLES)
  parser.add_argument('--hole_dir')
  parser.add_argument('--membership_file')
  parser.add_argument('--remove_neg_labels', action='store_true')
  parser.add_argument('--label_file')
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()
  if args.min_raw_price > MIN_RAW_PRICE:
    assert args.raw_price_dir is not None, (
        'must also specify --raw_price_dir since --min_raw_price is specified')
  else:
    assert args.raw_price_dir is None
  if args.max_volatility < MAX_VOLATILITY:
    assert args.volatility_dir is not None, (
        'must also specify --volatility_dir since --max_volatility is specified')
  else:
    assert args.volatility_dir is None
  if args.min_volumed > MIN_VOLUMED:
    assert args.volumed_dir is not None, (
        'must also specify --volumed_dir since --min_volumed is specified')
  else:
    assert args.volumed_dir is None
  if args.min_marketcap > MIN_MARKETCAP:
    assert args.marketcap_dir is not None, (
        'must also specify --marketcap_dir since --min_marketcap is specified')
  else:
    assert args.marketcap_dir is None
  if args.max_holes < MAX_HOLES:
    assert args.hole_dir is not None, (
        'must also specify --hole_dir since max_holes is specified')
  else:
    assert args.hole_dir is None
  if args.remove_neg_labels:
    assert args.label_file is not None, (
        'must also specify --label_file since --remove_neg_labels is specified')
  filterMetadata(args.input_file, args.min_raw_price, args.raw_price_dir,
                 args.max_volatility, args.volatility_dir,
                 args.min_volumed, args.volumed_dir, args.min_marketcap,
                 args.marketcap_dir, args.max_holes, args.hole_dir,
                 args.membership_file, args.remove_neg_labels,
                 args.label_file, args.output_file)

if __name__ == '__main__':
  main()

