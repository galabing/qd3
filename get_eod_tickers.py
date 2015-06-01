#!/usr/bin/python

import argparse

def getEodTickers(eod_file, ticker_file):
  tickers = set()
  with open(eod_file, 'r') as fp:
    while True:
      line = fp.readline()
      if line == '': break
      assert line[-1] == '\n'
      ticker, _, _, _, _, _, _, _, _, _, _, _, _, _ = line[:-1].split(',')
      tickers.add(ticker)
  tickers = sorted(tickers)
  with open(ticker_file, 'w') as fp:
    for ticker in tickers:
      print >> fp, ticker

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--eod_file', required=True)
  parser.add_argument('--ticker_file', required=True)
  args = parser.parse_args()
  getEodTickers(args.eod_file, args.ticker_file)

if __name__ == '__main__':
  main()

