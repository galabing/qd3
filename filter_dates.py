#!/usr/bin/python2.7

""" Example usage:
      ./filter_dates.py --input_file=./trading_days
                        --nth_day_of_week=2
                        --output_file=./filtered_days
    It will keep 2nd trading day of each week for output.
    Or,
      ./filter_dates.py --input_file=./trading_days
                        --nth_day_of_month=1
                        --output_file=./filtered_days
    It will keep 1st trading day of each month for output.
"""

import argparse
import datetime

def filterDates(args):
  assert args.nth_day_of_week > 0 or args.nth_day_of_month > 0
  assert args.nth_day_of_week == 0 or args.nth_day_of_month == 0
  with open(args.input_file, 'r') as fp:
    dates = sorted(fp.read().splitlines())
  counts = dict()  # (year, month/week) => count
  target = args.nth_day_of_week
  if args.nth_day_of_month > 0:
    target = args.nth_day_of_month
  with open(args.output_file, 'w') as fp:
    for date in dates:
      if args.nth_day_of_week > 0:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        year, week, _ = date_obj.isocalendar()
        key = (year, week)
      else:
        y, m, d = date.split('-')
        key = (y, m)
      count = counts.get(key, 0) + 1
      counts[key] = count
      if count == target:
        print >> fp, date

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', required=True)
  parser.add_argument('--nth_day_of_week', type=int, default=0)
  parser.add_argument('--nth_day_of_month', type=int, default=0)
  parser.add_argument('--output_file', required=True)
  filterDates(parser.parse_args())

if __name__ == '__main__':
  main()

