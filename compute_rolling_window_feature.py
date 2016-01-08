#!/usr/bin/python2.7

""" Example usage:
      ./compute_rolling_window_feature.py
          --input_dir=./volumed
          --window=5
          --method=mean
          --output_dir=./volumed_mean_5
"""

import argparse
import os
import util

SUPPORTED_METHODS = ['mean']

def computeRollingWindowFeature(args):
  assert args.window > 0
  tickers = sorted(os.listdir(args.input_dir))
  for ticker in tickers:
    dvalues = util.readKeyValueList('%s/%s' % (args.input_dir, ticker))
    dates = [dvalue[0] for dvalue in dvalues]
    values = [dvalue[1] for dvalue in dvalues]
    for i in range(len(dates)-1):
      assert dates[i] < dates[i+1]
    with open('%s/%s' % (args.output_dir, ticker), 'w') as fp:
      for i in range(args.window-1, len(dates)):
        wvalues = values[i-args.window+1:i+1]
        if args.method == 'mean':
          f = sum(wvalues)/args.window
        print >> fp, '%s\t%f' % (dates[i], f)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_dir', required=True)
  parser.add_argument('--window', type=int, required=True)
  parser.add_argument('--method', choices=SUPPORTED_METHODS, required=True)
  parser.add_argument('--output_dir', required=True)
  computeRollingWindowFeature(parser.parse_args())

if __name__ == '__main__':
  main()

