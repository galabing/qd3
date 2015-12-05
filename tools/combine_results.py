#!/usr/bin/python2.7

""" Combines ranking of stocks from multiple experimental result files.

    Example usage:
      ./combine_results.py --experiment_dir=./experiments
                           --experiments=Predict3,Predict6,Predict12,Predict24
                           --method=product
                           --output=./combined_result

    Result files are assumed to be at:
      <experiment_dir>/<experiment>/results/result

    For each prediction date (yyyy-mm), common stocks are collected from all
    experiments and their scores combined using specified method.  Stocks are
    then reranked and written to output.

    Output format:
      <yyyy-mm> <n> <exp1>:<n1> ... <expK>:<nK>
        <ticker1> <combined_score> <exp1>:<score1>,<rank>,<gain1> ... <expK>:<scoreK>,<rank>,<gainK>
        ...
"""

import argparse
import math

def readResults(result_file):
  results = dict()  # yyyy-mm => ticker => (score, rank, gain); rank is 0-based
  with open(result_file, 'r') as fp:
    lines = fp.read().splitlines()
  date = None
  rank = -1
  for line in lines:
    if line.startswith('date: '):
      date = line[6:]
      rank = 0
    else:
      empty, ticker, gain, score = line.split('\t')
      assert empty == ''
      gain = float(gain)
      score = float(score)
      assert date is not None
      if date not in results:
        results[date] = {ticker: (score, rank, gain)}
      else:
        assert ticker not in results[date]
        results[date][ticker] = (score, rank, gain)
      rank += 1
  return results

def combine(exp_results, date, ticker, method):
  scores = [exp_results[exp][date][ticker][0]
            for exp in exp_results.iterkeys()]
  ranks = [exp_results[exp][date][ticker][1]
           for exp in exp_results.iterkeys()]
  if method == 'product':
    return math.exp(sum([math.log(score) for score in scores]))
  if method == 'max_rank':
    return -max(ranks)
  assert False, method

def combineResults(args):
  experiments = args.experiments.split(',')
  print 'combining %d experiments: %s' % (len(experiments), experiments)

  exp_results = {exp: readResults('%s/%s/results/result' % (args.experiment_dir, exp))
                 for exp in experiments}

  common_dates = None
  for results in exp_results.itervalues():
    dates = set(results.keys())
    if common_dates is None:
      common_dates = dates
    else:
      common_dates &= dates
  common_dates = sorted(common_dates)
  print '%d common dates from %s to %s' % (len(common_dates), common_dates[0], common_dates[-1])

  with open(args.output, 'w') as fp:
    for date in common_dates:
      common_tickers = None
      ticker_counts = dict()
      for exp, results in exp_results.iteritems():
        tickers = set(results[date].keys())
        if common_tickers is None:
          common_tickers = tickers
        else:
          common_tickers &= tickers
        ticker_counts[exp] = len(tickers)
      print >> fp, '%s %d %s' % (date, len(common_tickers),
          ' '.join(['%s:%d' % (exp, ticker_counts[exp]) for exp in experiments]))

      combined = []  # [(ticker, combined_score) ...]
      for ticker in common_tickers:
        score = combine(exp_results, date, ticker, args.method)
        combined.append((ticker, score))
      combined.sort(key=lambda item: item[1], reverse=True)

      for ticker, combined_score in combined:
        items = {exp: exp_results[exp][date][ticker] for exp in experiments}
        print >> fp, '  %s %f %s' % (ticker, combined_score,
            ' '.join(['%s:%f,%d,%f' % (exp, items[exp][0], items[exp][1], items[exp][2])
                     for exp in experiments]))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--experiment_dir', required=True)
  parser.add_argument('--experiments', required=True)
  parser.add_argument('--method', default='product')
  parser.add_argument('--output', required=True)
  args = parser.parse_args()
  combineResults(args)

if __name__ == '__main__':
  main()

