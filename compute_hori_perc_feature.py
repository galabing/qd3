#!/usr/bin/python2.7

""" Computes horizontal percentile feature.

    Example usage:
      ./compute_hori_perc_feature.py --input_dir=./PE-ART
                                     --group_map_file=./sector_map
                                     --output_dir=./PE-ART_hp
                                     --rank

    For each ticker on each date, tickers within the same group as specified
    in --group_map_file (or all tickers if this is not set) are collected and
    percentile for this ticker is calculated.

    There are two ways of calculating percentile:
      1. using 0-based-rank divided by total count if --rank is set
      2. using (val - min) / (max - min) if --rank is not set

    Dates are aligned when calculating percentiles. For each month between min
    and max yyyy-mm-dd over all tickers, the first day of the month is selected
    and numbers from tickers on or before this date are collected for calculation.

    --group_map_file, if specified, is assumed to contain mapping between
    ticker and group names, eg: <ticker>\t<sector>.
"""

import argparse
import os
import util

EPS = 1e-5

def readGroups(group_map_file):
  with open(group_map_file, 'r') as fp:
    lines = fp.read().splitlines()
  groups = dict()  # group => tickers
  for line in lines:
    ticker, group = line.split('\t')
    if group not in groups:
      groups[group] = [ticker]
    else:
      groups[group].append(ticker)
  return groups

def computePercFeature(input_dir, tickers, rank, output_dir):
  # ticker => [[date, value] ...]
  # where date is the first yyyy-mm after data is published.
  # Dates are deduped (any yyyy-mm with more than one values available,
  # the latest one wins).
  data = dict()
  for ticker in tickers:
    dvalues = util.readKeyValueList('%s/%s' % (input_dir, ticker))
    udvalues = []
    for i in range(len(dvalues)):
      date = util.getNextYm(util.ymdToYm(dvalues[i][0]))
      if len(udvalues) > 0 and udvalues[-1][0] == date:
        udvalues[-1][1] = dvalues[i][1]
      else:
        if len(udvalues) > 0:
          assert udvalues[-1][0] < date
        udvalues.append([date, dvalues[i][1]])
    data[ticker] = udvalues

  min_date = '9999-99'
  max_date = '0000-00'
  for dvalues in data.itervalues():
    if len(dvalues) == 0:
      continue
    min_date = min(min_date, dvalues[0][0])
    max_date = max(max_date, dvalues[-1][0])

  percs = dict()  # date => [[ticker, value] ...]
  date = min_date
  while date <= max_date:
    percs[date] = []
    date = util.getNextYm(date)
  for ticker, dvalues in data.iteritems():
    for i in range(len(dvalues)):
      date, value = dvalues[i]
      if i < len(dvalues) - 1:
        # Populate value up to next date (not inclusive).
        next = dvalues[i+1][0]
      else:
        # Populate value up to max date (inclusive).
        next = util.getNextYm(max_date)
      while date < next:
        percs[date].append([ticker, value])
        date = util.getNextYm(date)

  # Calculate percentiles.
  for date, tvalues in percs.iteritems():
    assert len(tvalues) > 0
    # Use 0.5 if there is a single element.
    if len(tvalues) == 1:
      tvalues[0][1] = 0.5
      continue
    if rank:
      tvalues.sort(key=lambda item: item[1])
      for i in range(len(tvalues)):
        tvalues[i][1] = float(i)/len(tvalues)
    else:
      values = [item[1] for item in tvalues]
      maxv = max(values)
      minv = min(values)
      span = maxv - minv
      for i in range(len(tvalues)):
        if span < EPS:
          tvalues[i][1] = 0.5
        else:
          tvalues[i][1] = (tvalues[i][1] - minv) / span

  # Write output.
  data = dict()  # ticker => [[date, perc] ...]
  for date, tpercs in percs.iteritems():
    for ticker, perc in tpercs:
      if ticker not in data:
        data[ticker] = [[date, perc]]
      else:
        data[ticker].append([date, perc])
  for ticker, dpercs in data.iteritems():
    dpercs.sort(key=lambda item: item[0])
    with open('%s/%s' % (output_dir, ticker), 'w') as fp:
      for date, perc in dpercs:
        print >> fp, '%s\t%f' % (date, perc)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--group_map_file')
  parser.add_argument('--rank', action='store_true')
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  if args.group_map_file:
    groups = readGroups(args.group_map_file)
    for tickers in groups.itervalues():
      computePercFeature(args.input_dir, tickers, args.rank, args.output_dir)
    return

  tickers = os.listdir(args.input_dir)
  computePercFeature(args.input_dir, tickers, args.rank, args.output_dir)

if __name__ == '__main__':
  main()

