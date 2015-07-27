#!/usr/bin/python2.7

INPUT_FILE = '/Users/lnyang/lab/qd2/data/runs/20150701/raw/sf1/sf1.csv'
OUTPUT_FILE = '/Users/lnyang/lab/qd2/qd2/testdata/raw/sf1/sf1.csv'
TICKERS = {'A', 'AAPL', 'CCE', 'FB', 'GOOG', 'GOOGL', 'IBM', 'KMI', 'MEE', 'MFE'}

with open(INPUT_FILE, 'r') as ifp:
  with open(OUTPUT_FILE, 'w') as ofp:
    while True:
      line = ifp.readline()
      if line == '':
        break
      assert line[-1] == '\n'
      ticker = line[:line.find('_')]
      if ticker not in TICKERS:
        continue
      print >> ofp, line[:-1]

