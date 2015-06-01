#!/usr/bin/python

import argparse

def getSf1Tickers(sf1_file, ticker_file):
  tickers = set()
  with open(sf1_file, 'r') as fp:
    while True:
      line = fp.readline()
      if line == '': break
      assert line[-1] == '\n'
      item, _, _ = line[:-1].split(',')
      items = item.split('_')
      assert len(items) == 2 or len(items) == 3
      tickers.add(items[0])
  tickers = sorted(tickers)
  with open(ticker_file, 'w') as fp:
    for ticker in tickers:
      print >> fp, ticker

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sf1_file', required=True)
  parser.add_argument('--ticker_file', required=True)
  args = parser.parse_args()
  getSf1Tickers(args.sf1_file, args.ticker_file)

if __name__ == '__main__':
  main()

