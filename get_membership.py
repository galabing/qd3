#!/usr/bin/python2.7

""" Collects beginning-of-year memberships.
"""

import argparse

def isValid(ticker):
  # bad eg: MIR (M. R.)
  for s in ticker:
    if s < 'A' or s > 'Z':
      return False
  return True

def getMembership(input_file, output_dir):
  with open(input_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) > 1
  items = lines[0].split('\t')
  assert len(items) > 2
  assert items[0] == 'Ticker'
  assert items[1] == 'Company'
  years = {i: items[i] for i in range(2, len(items))}
  membership = {year: set() for year in years.values()}
  for i in range(1, len(lines)):
    items = lines[i].split('\t')
    assert len(items) == len(years) + 2
    ticker = items[0]
    if not isValid(ticker):
      print 'skipping bad ticker: %s' % ticker
      continue
    for j in range(2, len(items)):
      if items[j].strip() == 'X':
        membership[years[j]].add(ticker)
  for year in years.values():
    with open('%s/%s' % (output_dir, year), 'w') as fp:
      for ticker in sorted(membership[year]):
        print >> fp, ticker

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_file', required=True,
                      help='tsv file of ticker-year membership')
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  getMembership(args.input_file, args.output_dir)

if __name__ == '__main__':
  main()

