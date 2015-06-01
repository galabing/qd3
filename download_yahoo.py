#!/usr/bin/python

import argparse
import os
import util

WGET = '/usr/local/bin/wget'
BASE_URL = 'http://real-chart.finance.yahoo.com/table.csv?s='
RETRIES = 3

def download(ticker_file, download_dir, overwrite):
  with open(ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  for ticker in tickers:
    download_file = '%s/%s.csv' % (download_dir, ticker)
    if os.path.isfile(download_file) and not overwrite:
      continue
    cmd = '%s --quiet "%s%s" -O %s' % (
        WGET, BASE_URL, ticker, download_file)
    for i in range(RETRIES):
      result = util.run(cmd, check=False)
      if result == 0:
        break
      if os.path.isfile(download_file):
        os.remove(download_file)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--download_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  args = parser.parse_args()
  download(args.ticker_file, args.download_dir, args.overwrite)

if __name__ == '__main__':
  main()

