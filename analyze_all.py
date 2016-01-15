#!/usr/bin/python2.7

# Adapted from qd (Q-analyze.py and analyze_results.py)

from config import *
import argparse
import math

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
    #year, month, day = date.split('-')
    #date = '%s-%s' % (year, month)
    assert date not in market
    market[date] = float(gain)
  return market

def prepTopBot(data, ks):
  assert len(ks) > 0
  gain_map = dict()  # yyyy-mm => gains
  precision_map = dict()  # yyyy-mm => precisions
  for date, items in data.iteritems():
    assert date not in gain_map
    assert date not in precision_map
    gains = [0.0 for k in ks]
    precisions = [0.0 for k in ks]
    items = [item[1] for item in items]
    bitems = []  # 1 if positive gain, 0 otherwise
    for item in items:
      if item > 0:
        bitems.append(1.0)
      else:
        bitems.append(0.0)
    assert len(bitems) == len(items)
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
      gains[i] = sum(items[p:q]) / (q-p)
      precisions[i] = sum(bitems[p:q]) / (q-p)
    gain_map[date] = gains
    precision_map[date] = precisions
  return gain_map, precision_map

def getStats(value_map, nk):
  mean = [0.0 for i in range(nk)]
  std = [0.0 for i in range(nk)]
  sharpe = [0.0 for i in range(nk)]
  for i in range(nk):
    values = [value[i] for value in value_map.itervalues()]
    mean[i] = sum(values)/len(values)
    diff = [value - mean[i] for value in values]
    std[i] = math.sqrt(sum([d**2 for d in diff])/len(diff))
    sharpe[i] = mean[i]/std[i]
  return mean, std, sharpe

def writeOneTopBot(value_map, ks, output_file):
  mean, std, sharpe = getStats(value_map, len(ks))
  with open(output_file, 'w') as fp:
    print >> fp, '\t'.join(['date'] + ['%d' % k for k in ks])
    for date in sorted(value_map.keys()):
      print >> fp, '\t'.join([date] + ['%f' % value for value in value_map[date]])
    print >> fp, '\t'.join(['mean'] + ['%f' % m for m in mean])
    print >> fp, '\t'.join(['std'] + ['%f' % s for s in std])
    print >> fp, '\t'.join(['sharpe'] + ['%f' % s for s in sharpe])

def writeTopBot(data, ks, gain_file, precision_file):
  gain_map, precision_map = prepTopBot(data, ks)
  writeOneTopBot(gain_map, ks, gain_file)
  writeOneTopBot(precision_map, ks, precision_file)

def writeBuckets(data, buckets, output_file):
  assert buckets > 0
  total_histogram = [0.0 for i in range(buckets)]
  total_months = 0
  histograms = dict()  # year => histogram, months
  for date, items in data.iteritems():
    year, m, d = date.split('-')
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
               market, output_file):
  buys = dict()  # date => [[ticker, gain, score], ...]
  record = []  # [[ticker, buy_date, sale_date], ...]
  for date in sorted(data.keys()):
    items = data[date]
    updateTrans(date, items, hold_period, max_look, max_pick, max_hold,
                buys, record)
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

def writeTopK(data, market, topk, output_file):
  with open(output_file, 'w') as fp:
    print >> fp, '\t'.join([
        'date', 'ticker', 'score', 'gain', 'market'])
    for date in sorted(data.keys()):
      items = data[date]
      assert len(items) >= topk
      market_gain = '-'
      if market is not None:
        market_gain = '%.2f%%' % (market[date] * 100)
      for i in range(topk):
        ticker, gain, score = items[i]
        print >> fp, '\t'.join([
            date, ticker, '%.4f' % score, '%.2f%%' % (gain*100), market_gain])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--result_file', required=True)
  parser.add_argument('--hold_period', type=int, default=-1)
  parser.add_argument('--market_gain_file')
  parser.add_argument('--analyze_dir', required=True)
  parser.add_argument('--skip_trans', action='store_true')
  args = parser.parse_args()

  data = readData(args.result_file)
  market = None
  if args.market_gain_file:
    market = readMarketGains(args.market_gain_file)

  writeTopBot(data, KS,
      '%s/gain_topbot.tsv' % args.analyze_dir,
      '%s/precision_topbot.tsv' % args.analyze_dir)

  for buckets in BUCKETS_LIST:
    writeBuckets(data, buckets,
                 '%s/bucket-%d.tsv' % (args.analyze_dir, buckets))

  if not args.skip_trans:
    assert args.hold_period > 0, 'must specify --hold_period unless --skip_trans'
    for max_look, max_pick, max_hold in TRADE_CONFIGS:
      output_file = '%s/trade-ml%d-mp%d-mh%d.tsv' % (
          args.analyze_dir, max_look, max_pick, max_hold)
      writeTrans(data, args.hold_period, max_look, max_pick, max_hold,
                 market, output_file)

  writeTopK(data, market, TOPK, '%s/top%d.tsv' % (args.analyze_dir, TOPK))

if __name__ == '__main__':
  main()

