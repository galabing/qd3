#!/usr/bin/python2.7

""" Computes volatility.

    Example usage:
      ./compute_volatility.py --price_dir=./adjprice
                              --k=24
                              --volatility_dir=./volatility/24
"""

import argparse
import math
import os
import util

EPS = 0.01  # to prevent divide-by-zero in calculating gains

def computeStd(values):
  if len(values) == 0:
    return 0.0
  mean = sum(values) / len(values)
  std = 0.0
  for value in values:
    std += (value - mean)**2
  return math.sqrt(std / len(values))

def computeVolatility(price_dir, k, volatility_dir):
  assert k > 0
  tickers = sorted(os.listdir(price_dir))
  for ticker in tickers:
    price_file = '%s/%s' % (price_dir, ticker)
    dprices = util.readKeyValueList(price_file)
    with open('%s/%s' % (volatility_dir, ticker), 'w') as fp:
      for i in range(len(dprices)):
        prices = [dprices[j][1] for j in range(max(0,i-k), i+1)]
        gains = [(prices[j+1] - prices[j]) / (prices[j] + EPS) for j in range(len(prices) - 1)]
        volatility = computeStd(gains)
        print >> fp, '%s\t%f' % (dprices[i][0], volatility)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--k', type=int, required=True)
  parser.add_argument('--volatility_dir', required=True)
  args = parser.parse_args()
  computeVolatility(args.price_dir, args.k, args.volatility_dir)

if __name__ == '__main__':
  main()

