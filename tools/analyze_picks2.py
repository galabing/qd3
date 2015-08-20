#!/usr/bin/python2.7

""" Analyzes price trend for top picks.

    Example usage:
      ./analyze_picks2.py --result_file=./result
                          --years=2011,2012
                          --topk=1
                          --price_dir=./yahoo/price
                          --output_dir=./output
"""

import argparse

def getNumbers(number_str):
  return [int(number) for number in number_str.split(',') if number != '']

def wantDate(date, years):
  if len(years) == 0:
    return True
  year, month = date.split('-')
  return int(year) in years

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

def analyzePicks(result_file, years, topk, price_dir, output_dir):
  years = set(getNumbers(years))
  if len(years) == 0:
    print 'using stock picks from all years'
  else:
    print 'using stock picks from years: %s' % years

  picks = readPicks(result_file, years, topk)  # date => tickers
  print 'read picks for %d dates' % len(picks)

  picks2 = dict()  # ticker => date set
  for date, tickers in picks.iteritems():
    for ticker in tickers:
      if ticker not in picks2:
        picks2[ticker] = {date}
      else:
        picks2[ticker].add(date)

  print 'reading price data for %d tickers' % len(picks2)

  prices = readPrices(price_dir, picks2.keys())  # ticker => date => price
  print 'read price data for %d tickers' % len(prices)

  for ticker, buy_dates in picks2.iteritems():
    price = prices[ticker]
    dates = sorted(price.keys())
    with open('%s/%s.tsv' % (output_dir, ticker), 'w') as fp:
      print >> fp, '\t'.join(['date', 'price', 'buy'])
      for date in dates:
        if date in buy_dates:
          print >> fp, '\t'.join([date, '', '%.2f' % price[date]])
        else:
          print >> fp, '\t'.join([date, '%.2f' % price[date], ''])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--result_file', required=True)
  parser.add_argument('--years', default='')
  parser.add_argument('--topk', type=int, default=1)
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  analyzePicks(args.result_file, args.years, args.topk,
               args.price_dir, args.output_dir)

if __name__ == '__main__':
  main()

