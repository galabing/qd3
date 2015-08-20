#!/usr/bin/python2.7

""" Analyzes price trend for top picks.

    Example usage:
      ./analyze_picks.py --result_file=./result
                         --years=2014,2015
                         --topk=5
                         --price_dir=./yahoo/price
                         --windows=1,2,3,6,12
                         --output_file=./output
"""

import argparse

def getNumbers(number_str):
  return [int(number) for number in number_str.split(',') if number != '']

def wantDate(date, years):
  if len(years) == 0:
    return True
  year, month = date.split('-')
  return int(year) in years

def getPreviousYm(ym, k=1):
  assert k >= 0
  y, m = ym.split('-')
  y = int(y)
  m = int(m)
  y -= int(k/12)
  m -= k % 12
  if m < 1:
    m += 12
    y -= 1
  return '%02d-%02d' % (y, m)

def readPrice(price_dir, ticker):
  with open('%s/%s' % (price_dir, ticker), 'r') as fp:
    lines = fp.read().splitlines()
  price = dict()
  for line in lines:
    date, value = line.split('\t')
    year, month, day = date.split('-')
    key = '%s-%s' % (year, month)
    assert key not in price
    price[key] = float(value)
  return price

def readPrices(price_dir, tickers):
  prices = dict()
  for ticker in tickers:
    prices[ticker] = readPrice(price_dir, ticker)
  return prices

def readPicks(result_file, years, topk):
  assert topk > 0

  picks = dict()  # date => tickers
  with open(result_file, 'r') as fp:
    date = None
    while True:
      line = fp.readline()
      if line == '':
        break
      assert line.endswith('\n')
      line = line[:-1]

      # A new block (date) starts.
      if line.startswith('date:'):
        _, next_date = line.split(' ')
        if date is not None:
          assert next_date > date  # dates must be in order
          assert len(picks[date]) == topk  # must be done with previous block
        # If next_date is wanted, update date and init picks[date]; otherwise
        # set date to None and subsequent lines in this block will be skipped.
        if wantDate(next_date, years):
          date = next_date
          picks[date] = []
        else:
          date = None
        continue

      # Not a year we care about.
      if date is None:
        continue

      # Have collected enough picks for current block.
      if len(picks[date]) >= topk:
        continue

      # Collect one more topk pick for current block.
      empty, ticker, _, _ = line.split('\t')
      assert empty == ''
      assert ticker not in picks[date]
      picks[date].append(ticker)

  return picks

def analyzePicks(result_file, years, topk, price_dir, windows, output_file):
  years = set(getNumbers(years))
  if len(years) == 0:
    print 'using stock picks from all years'
  else:
    print 'using stock picks from years: %s' % years

  windows = getNumbers(windows)
  assert len(windows) > 0
  windows.sort()
  assert windows[0] > 0
  for i in range(1, len(windows)):
    assert windows[i] > windows[i - 1]
  print 'analyzing trend for time windows: %s' % windows

  picks = readPicks(result_file, years, topk)  # date => tickers
  print 'read picks for %d dates' % len(picks)

  tickers = set()
  for v in picks.itervalues():
    for ticker in v:
      tickers.add(ticker)
  print 'reading price data for %d tickers' % len(tickers)

  prices = readPrices(price_dir, tickers)  # ticker => date => price
  print 'read price data for %d tickers' % len(prices)

  dates = sorted(picks.keys())
  with open(output_file, 'w') as fp:
    print >> fp, '\t'.join(['date', 'ticker', 'current'] +
                           ['-%dm' % window for window in windows])
    for date in dates:
      tickers = picks[date]
      for ticker in tickers:
        price = prices[ticker]
        trend = ['%.2f' % price[date]]
        for window in windows:
          pdate = getPreviousYm(date, window)
          if pdate in price:
            trend.append('%.2f' % price[pdate])
          else:
            trend.append('-')
        print >> fp, '\t'.join([date, ticker] + trend)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--result_file', required=True)
  parser.add_argument('--years', default='')
  parser.add_argument('--topk', type=int, default=5)
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--windows', default='1,2,3,6,12')
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()
  analyzePicks(args.result_file, args.years, args.topk,
               args.price_dir, args.windows, args.output_file)

if __name__ == '__main__':
  main()

