#!/usr/bin/python2.7

# Adapted from qd (Q-analyze.py and analyze_results.py)

from config import *
import argparse

def readData(input_file):
  # date => [[ticker, gain, score] ...]
  with open(input_file, 'r') as fp:
    lines = fp.read().splitlines()
  data = dict()
  for line in lines:
    if line.startswith('date:'):
      tmp, date = line.split(' ')
      assert date not in data
      data[date] = []
      continue
    empty, ticker, gain, score = line.split('\t')
    assert empty == ''
    gain = float(gain)
    score = float(score)
    if len(data[date]) > 0:
      assert score <= data[date][-1][2]
    data[date].append([ticker, gain, score])
  # hacky way to get rid of all 0 gains (available in the future)
  future_dates = []
  for date, items in data.iteritems():
    all_zero = True
    for item in items:
      if item[1] != 0.0:
        all_zero = False
        break
    if all_zero:
      future_dates.append(date)
  for date in future_dates:
    del data[date]
  return data

def readMarketGains(market_gain_file):
  with open(market_gain_file, 'r') as fp:
    lines = fp.read().splitlines()
  market = dict()  # yyyy-mm => gain
  for line in lines:
    date, gain = line.split('\t')
    year, month, day = date.split('-')
    date = '%s-%s' % (year, month)
    assert date not in market
    market[date] = float(gain)
  return market

def writeKs(data, ks, output_file):
  assert len(ks) > 0
  total_gains = [0.0 for k in ks]
  total_months = 0
  gains_map = dict()  # year => gains, months
  for date, items in data.iteritems():
    items = [item[1] for item in items]
    year, m = date.split('-')
    if year not in gains_map:
      gains_map[year] = [[0.0 for k in ks], 0]
    gains_map[year][1] += 1
    gains = gains_map[year][0]
    for i in range(len(ks)):
      k = ks[i]
      if k > 0:
        p = 0
        q = min(len(items), k)
      elif k == 0:
        p = 0
        q = len(items)
      else:
        p = max(0, len(items) + k)
        q = len(items)
      gain = sum(items[p:q]) / (q-p)
      gains[i] += gain
      total_gains[i] += gain
    total_months += 1
  for gains, months in gains_map.itervalues():
    for i in range(len(gains)):
      gains[i] /= months
  for i in range(len(ks)):
    total_gains[i] /= total_months
  with open(output_file, 'w') as fp:
    print >> fp, 'year\t%s\tmonths' % ('\t'.join(['%d' % k for k in ks]))
    for year in sorted(gains_map.keys()):
      gains, months = gains_map[year]
      print >> fp, '%s\t%s\t%d' % (year, '\t'.join(['%f' % g for g in gains]),
                                   months)
    print >> fp, 'all\t%s\t%d' % ('\t'.join(['%f' % g for g in total_gains]),
                                  total_months)

def writeBuckets(data, buckets, output_file):
  assert buckets > 0
  total_histogram = [0.0 for i in range(buckets)]
  total_months = 0
  histograms = dict()  # year => histogram, months
  for date, items in data.iteritems():
    year, m = date.split('-')
    if year not in histograms:
      histograms[year] = [[0.0 for i in range(buckets)], 0]
    histograms[year][1] += 1
    histogram = histograms[year][0]

    gains = [item[1] for item in items]
    bucket_size = int(len(gains)/buckets)
    sizes = [bucket_size for i in range(buckets)]
    extra = len(gains) % buckets
    for i in range(buckets - extra, buckets):
      sizes[i] += 1
    assert sum(sizes) == len(gains)

    p = 0
    for i in range(buckets):
      size = sizes[i]
      gain = sum(gains[p:p+size]) / size
      histogram[i] += gain
      total_histogram[i] += gain
      p += size
    total_months += 1

  for histogram, months in histograms.itervalues():
    for i in range(buckets):
      histogram[i] /= months
  for i in range(buckets):
    total_histogram[i] /= total_months

  with open(output_file, 'w') as fp:
    print >> fp, 'year\t%s\tavg\tmonths' % (
        '\t'.join(['B%d' % (i+1) for i in range(buckets)]))
    for year in sorted(histograms.keys()):
      histogram, months = histograms[year]
      print >> fp, '%s\t%s\t%f\t%d' % (
          year, '\t'.join(['%f' % h for h in histogram]),
          sum(histogram)/len(histogram), months)
    print >> fp, 'all\t%s\t%f\t%d' % (
        '\t'.join(['%f' % h for h in total_histogram]),
        sum(total_histogram)/len(total_histogram), total_months)

def getSaleDate(buy_date, months):
  year, month = buy_date.split('-')
  year = int(year)
  month = int(month)
  year += int(months / 12)
  month += months % 12
  if month > 12:
    year += 1
    month -= 12
  return '%04d-%02d' % (year, month)

def updateTrans(date, items, months, max_look, max_pick, max_hold, buys, record):
  tickers = [item[0] for item in record if item[2] > date]
  holds = dict()  # ticker => num holdings
  for ticker in tickers:
    if ticker not in holds:
      holds[ticker] = 1
    else:
      holds[ticker] += 1
  i, j = 0, 0
  trans = []
  while i < abs(max_pick) and (max_look < 0 or j < max_look) and j < len(items):
    if max_pick > 0:
      ticker, gain, score = items[j]
    else:
      ticker, gain, score = items[-1 - j]
    if ticker in holds and max_hold > 0 and holds[ticker] >= max_hold:
      j += 1
      continue
    trans.append([ticker, gain, score])
    record.append([ticker, date, getSaleDate(date, months)])
    i += 1
    j += 1
  assert date not in buys
  buys[date] = trans

def writeTrans(data, hold_period, max_look, max_pick, max_hold,
               market_gain_file, output_file):
  buys = dict()  # date => [[ticker, gain, score], ...]
  record = []  # [[ticker, buy_date, sale_date], ...]
  for date in sorted(data.keys()):
    items = data[date]
    updateTrans(date, items, hold_period, max_look, max_pick, max_hold,
                buys, record)
  market = None
  if market_gain_file:
    market = readMarketGains(market_gain_file)
  with open(output_file, 'w') as fp:
    print >> fp, '\t'.join([
        'date', 'buys', 'total_hold', 'max_hold',
        'mh_ticker', 'gain', 'market'])
    for date in sorted(buys.keys()):
      trans = buys[date]
      gain = 0.0
      if len(trans) > 0:
        gain = sum([t[1] for t in trans])/len(trans)
      hold = [item[0] for item in record if item[1] <= date and item[2] > date]
      count = dict()  # ticker => count
      for ticker in hold:
        if ticker not in count:
          count[ticker] = 1
        else:
          count[ticker] += 1
      max_hold = 0
      mh_ticker = None
      for ticker, c in count.iteritems():
        if c > max_hold:
          max_hold = c
          mh_ticker = ticker
      market_gain = '-'
      if market is not None:
        market_gain = '%.2f%%' % (market[date] * 100)
      print >> fp, '\t'.join([
          date, str(len(trans)), str(len(hold)), str(max_hold), mh_ticker,
          '%.2f%%' % (gain*100), market_gain])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--result_file', required=True)
  parser.add_argument('--hold_period', type=int, required=True)
  parser.add_argument('--market_gain_file')
  parser.add_argument('--analyze_dir', required=True)
  args = parser.parse_args()

  data = readData(args.result_file)
  writeKs(data, KS, '%s/topbot.tsv' % args.analyze_dir)
  for buckets in BUCKETS_LIST:
    writeBuckets(data, buckets,
                 '%s/bucket-%d.tsv' % (args.analyze_dir, buckets))
  for max_look, max_pick, max_hold in TRADE_CONFIGS:
    output_file = '%s/trade-ml%d-mp%d-mh%d.tsv' % (
        args.analyze_dir, max_look, max_pick, max_hold)
    writeTrans(data, args.hold_period, max_look, max_pick, max_hold,
               args.market_gain_file, output_file)

if __name__ == '__main__':
  main()

