#!/usr/bin/python2.7

import argparse
import bisect
import datetime
import os

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

  #print 'loaded %d tickers, min date: %s, max date: %s' % (
  #    len(data_map), min_date, max_date)

  with open(args.output_file, 'w') as fp:
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
      if float(trading_count)/total_count >= args.threshold:
        print >> fp, date
      date_obj += step

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--raw_dir', required=True)
  parser.add_argument('--min_year', default='2000')
  parser.add_argument('--threshold', type=float, default=0.99)
  parser.add_argument('--output_file', required=True)
  getTradingDays(parser.parse_args())

if __name__ == '__main__':
  main()

