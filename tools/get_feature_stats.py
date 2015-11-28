#!/usr/bin/python

import os

INFO_DIR = '/home/lnyang/lab/qd2/data/runs/20151101/feature_info'
STATS_FILE = '/home/lnyang/tmp/feature_stats.tsv'
EXCLUDED_PREFIXES = [
    'log',
]

INPUT_HEADERS = ['year', 'count', 'total', 'coverage', 'avg', 'min', '1perc', '10perc',
                 '25perc', '50perc', '75perc', '90perc', '99perc', 'max']
OUTPUT_HEADS = ['feature\\stats', 'coverage', 'avg', '1perc', '50perc', '99perc']

index = {key: INPUT_HEADERS.index(key) for key in ['coverage', 'avg', '1perc', '50perc', '99perc']}

candidates = os.listdir(INFO_DIR)
features = []
for feature in candidates:
  excluded = False
  for prefix in EXCLUDED_PREFIXES:
    if feature.startswith(prefix):
      excluded = True
      break
  if not excluded:
    features.append(feature)
features.sort()
print 'processing %d features' % len(features)

with open(STATS_FILE, 'w') as fp:
  print >> fp, '\t'.join(OUTPUT_HEADERS)
  for feature in features:
    info_file = '%s/%s' % (INFO_DIR, feature)
    with open(info_file, 'r') as ifp:
      lines = ifp.read().splitlines()
    assert len(lines) > 2
    assert lines[1] == '\t'.join(INPUT_HEADERS)
    coverages = []
    avgs = []
    perc1s = []
    perc50s = []
    perc99s = []
    for i in range(2, len(lines)):
      items = lines[i].split('\t')
      coverage = items[index['coverage']]
      avg = items[index['avg']]
      perc1 = items[index['perc1']]
      perc50 = items[index['perc50']]
      perc99 = items[index['perc99']]
      assert coverage.endswith('%')
      coverages.append(float(coverage[:-1]))
      avg.append(float(avg))
      perc1s.append(float(perc1))
      perc50s.append(float(perc50))
      perc99s.append(float(perc99))
    coverage = sum(coverages)/len(coverages)
    avg = sum(avgs)/len(avgs)
    perc1 = sum(perc1s)/len(perc1s)
    perc50 = sum(perc50s)/len(perc1s)
    perc99 = sum(perc99s)/len(perc99s)
    print >> fp, '%s\t%.2f%%\t%.6f\t%.6f\t%.6f\t%.6f' % (
        feature, coverage, avg, perc1, perc50, perc99)

