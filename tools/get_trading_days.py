#!/usr/bin/python2.7

import argparse
import bisect
import datetime
import os

THRESHOLDS = [0.9, 0.95, 0.99]

def getTradingDays(args):
  tickers = sorted([f[:f.rfind('.')] for f in os.listdir(args.raw_dir)
                    if f.endswith('.csv')])

  data_map = dict()  # ticker => {dates}
  range_map = dict()  # ticker => (min_date, max_date)
  min_date = '9999-99-99'
  max_date = '0000-00-00'

  for ticker in tickers:
    with open('%s/%s.csv' % (args.raw_dir, ticker), 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
    dates = set()
    for i in range(1, len(lines)):
      date = lines[i][:lines[i].find(',')]
      y, m, d = date.split('-')
      if y < args.min_year:
        continue
      dates.add(date)
      min_date = min(min_date, date)
      max_date = max(max_date, date)
    if len(dates) == 0:
      continue
    data_map[ticker] = dates
    range_map[ticker] = (min(dates), max(dates))

  print 'loaded %d tickers, min date: %s, max date: %s' % (
      len(data_map), min_date, max_date)

  count_map = dict()  # date => (trading_count, total_count)
  min_date_obj = datetime.datetime.strptime(min_date, '%Y-%m-%d')
  max_date_obj = datetime.datetime.strptime(max_date, '%Y-%m-%d')
  assert min_date_obj <= max_date_obj
  step = datetime.timedelta(1)
  date_obj = min_date_obj
  while date_obj <= max_date_obj:
    date = date_obj.strftime('%Y-%m-%d')
    trading_count = 0
    total_count = 0
    for ticker, dates in data_map.iteritems():
      min_date, max_date = range_map[ticker]
      if date < min_date or date > max_date:
        continue
      total_count += 1
      if date in dates:
        trading_count += 1
    count_map[date] = (trading_count, total_count)
    date_obj += step

  year_count_map = dict()  # year => [(date, trading_count, total_count, ratio)]
  for date, counts in count_map.iteritems():
    trading_count, total_count = counts
    y, m, d = date.split('-')
    if y not in year_count_map:
      year_count_map[y] = [(date, trading_count, total_count, float(trading_count)/total_count)]
    else:
      year_count_map[y].append((date, trading_count, total_count, float(trading_count)/total_count))
  for year, items in year_count_map.iteritems():
    year_count_map[year] = sorted(items, key=lambda item: item[3], reverse=True)

  for year in sorted(year_count_map.keys()):
    items = year_count_map[year]
    index = -1
    if len(items) >= args.target_days:
      index = args.target_days - 1
    print '%s: %d days total, threshold: %s' % (year, len(items), items[index])
    ratios = [item[3] for item in items]
    ratios.reverse()
    for threshold in THRESHOLDS:
      index = bisect.bisect_left(ratios, threshold)
      print '  %f: %d - %s' % (ratios[index], len(items) - index, items[len(items) - index - 1])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--min_year', default='2000')
  parser.add_argument('--target_days', type=int, default=252)
  getTradingDays(parser.parse_args())

if __name__ == '__main__':
  main()

