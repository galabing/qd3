#!/usr/bin/python

input_file = '/Users/lnyang/tmp/SP500-membership.tsv'
output_dir = '/Users/lnyang/tmp/SP500-membership'

with open(input_file, 'r') as fp:
  lines = fp.read().splitlines()
membership = dict()  # year => set of tickers

assert len(lines) > 1
items = lines[0].split('\t')
assert len(items) > 2
assert items[0] == 'Ticker'
assert items[1] == 'Company'

index = dict()  # index => year
for i in range(2, len(items)):
  year = items[i]
  index[i] = year
  membership[year] = set()

for i in range(1, len(lines)):
  items = lines[i].split('\t')
  assert len(items) == len(membership) + 2
  ticker = items[0]
  for j in range(2, len(items)):
    if items[j] == 'X':
      membership[index[j]].add(ticker)

for year, tickers in membership.iteritems():
  with open('%s/%s' % (output_dir, year), 'w') as fp:
    for ticker in sorted(tickers):
      print >> fp, ticker
  print 'year: %s, %d tickers' % (year, len(tickers))

