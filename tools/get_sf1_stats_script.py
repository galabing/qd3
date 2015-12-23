#!/usr/bin/python2.7

""" Gets stats for SF1 features.

    It reads SF1 raw file (eg, SF1_20151219.csv) and collects values
    for specified feature.  It bins values by ticker, year and keeps
    the last value of each year for each ticker.  For each year, stats
    like mean and deciles are computed.
"""

SF1_FILE = '/Users/lnyang/lab/qd2/data/runs/20151201/raw/sf1/SF1_20151219.csv'
FEATURE = 'MARKETCAP'
OUTPUT_FILE = '//Users/lnyang/lab/qd2/tmp/%s-stats' % FEATURE

data = dict()  # year => ticker => [date, value]
with open(SF1_FILE, 'r') as fp:
  while True:
    line = fp.readline()
    if line == '':
      break
    assert line.endswith('\n')
    key, date, value = line[:-1].split(',')
    p = key.find('_')
    assert p > 0
    ticker = key[:p]
    feature = key[p+1:]
    if feature != FEATURE:
      continue
    y, m, d = date.split('-')
    value = float(value)
    if y not in data:
      data[y] = {ticker: [date, value]}
    elif ticker not in data[y]:
      data[y][ticker] = [date, value]
    elif date > data[y][ticker][0]:
      data[y][ticker] = [date, value]

for key, value in data.iteritems():
  data[key] = sorted([item[1] for item in value.values()])
with open(OUTPUT_FILE, 'w') as fp:
  for year in sorted(data.keys()):
    values = data[year]
    mean = sum(values)/len(values)
    deciles = ['%d: %f' % (i, values[min(len(values)-1, int(len(values)*i/10.0))])
               for i in range(11)]
    print >> fp, '%s: mean = %f' % (year, mean)
    print >> fp, '  deciles: %s' % (', '.join(deciles))

