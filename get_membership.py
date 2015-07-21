#!/usr/bin/python2.7

""" Collects stock membership.

    ./get_membership.py --boy_file=./SP500-boy.tsv
                        --change_file=./SP500-changes.tsv
                        --membership_file=./SP500-membership

    In output file --membership_file, each line contains a ticker
    and ranges of time during which it's part of the membership.
"""

import argparse
import datetime

CHANGE_HEADERS = [
    'Company',
    'Ticker',
    'Old Name & Ticker',
    'Company',
    'Ticker',
    'Old Name & Ticker',
    'Date',
    'Year',
    '', '', '', '', '', '', '', '', '',
]

FROM_FORMAT = '%B %d, %Y'
TO_FORMAT = '%Y-%m-%d'

BAD_DATES = {
    # PCS is not in boy['2000'] but dropped on 2004-04-22.
    '2004-04-22',
}

def isValid(ticker):
  # bad eg: MIR (M. R.)
  if ticker == '':
    return False
  for s in ticker:
    if s < 'A' or s > 'Z':
      return False
  return True

def getBoy(boy_file):
  with open(boy_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 1
  items = lines[0].split('\t')
  assert len(items) > 2
  assert items[0] == 'Ticker'
  assert items[1] == 'Company'
  years = {i: items[i] for i in range(2, len(items))}
  boy = {year: set() for year in years.values()}
  for i in range(1, len(lines)):
    items = lines[i].split('\t')
    assert len(items) == len(years) + 2
    ticker = items[0]
    if not isValid(ticker):
      continue
    for j in range(2, len(items)):
      if items[j].strip() == 'X':
        boy[years[j]].add(ticker)
  return boy

def getChanges(change_file):
  with open(change_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 2
  assert lines[1] == '\t'.join(CHANGE_HEADERS), (
      'unexpected header: %s' % lines[1].split('\t'))
  changes = dict()  # date => [added list, dropped list]
  for i in range(2, len(lines)):
    (_, added_ticker, _, _, dropped_ticker, _, date, year,
     _, _, _, _, _, _, _, _, _) = lines[i].split('\t')
    date = datetime.datetime.strptime(date, FROM_FORMAT).strftime(TO_FORMAT)
    assert date.startswith(year)
    if added_ticker == dropped_ticker:
      continue
    if date not in changes:
      changes[date] = [[], []]
    if isValid(added_ticker):
      changes[date][0].append(added_ticker)
    if isValid(dropped_ticker):
      changes[date][1].append(dropped_ticker)
  return changes

def check(boy, changes):
  min_year = min(boy.keys())
  tickers = set([ticker for ticker in boy[min_year]])

  dates = sorted(changes.keys())
  year = min_year
  for date in dates:
    y, m, d = date.split('-')
    if y < year:
      continue
    if y > year:
      year = y
      expected = boy[year]
      extra = tickers - expected
      missing = expected - tickers
      if len(extra) > 0 or len(missing) > 0:
        print 'warning: failed check for year: %s' % year
        print '  extra: %s' % extra
        print '  missing: %s' % missing
    added_tickers, dropped_tickers = changes[date]
    for added_ticker in added_tickers:
      if added_ticker in tickers:
        print 'warning: %s: %s cannot be added' % (
            date, added_ticker)
      else:
        #print '%s: add %s' % (date, added_ticker)
        tickers.add(added_ticker)
    for dropped_ticker in dropped_tickers:
      if dropped_ticker not in tickers:
        print 'warning: %s: %s cannot be dropped' % (
            date, dropped_ticker)
      else:
        #print '%s: drop %s' % (date, dropped_ticker)
        tickers.remove(dropped_ticker)

def getMembership(boy_file, change_file, membership_file):
  boy = getBoy(boy_file)
  changes = getChanges(change_file)
  check(boy, changes)

  tickers = set()
  for ts in boy.itervalues():
    tickers.update(ts)
  tickers = sorted(tickers)
  dates = sorted(changes.keys())

  min_year = min(boy.keys())
  min_date = '%s-00-00' % min_year
  max_date = '9999-99-99'
  with open(membership_file, 'w') as fp:
    for ticker in tickers:
      periods = []
      added = None
      if ticker in boy[min_year]:
        added = min_date
      for date in dates:
        if date < min_date:
          continue
        if date in BAD_DATES:
          continue
        added_tickers, dropped_tickers = changes[date]
        if ticker in added_tickers:
          assert added is None, '%s: add %s' % (date, ticker)
          added = date
        if ticker in dropped_tickers:
          assert added is not None, '%s: drop %s' % (date, ticker)
          periods.append((added, date))
          added = None
      if added is not None:
        periods.append((added, max_date))
      print >> fp, '%s\t%s' % (ticker,
          ' '.join(['%s,%s' % (added, dropped)
                    for added, dropped in periods]))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--boy_file', required=True,
                      help='tsv file of beginning-of-year membership')
  parser.add_argument('--change_file', required=True)
  parser.add_argument('--membership_file', required=True)
  args = parser.parse_args()
  getMembership(args.boy_file, args.change_file, args.membership_file)

if __name__ == '__main__':
  main()

