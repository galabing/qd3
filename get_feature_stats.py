#!/usr/bin/python2.7

# Adapted from qd/scripts/feature_stats.py

import argparse
import os

INFO_HEADER = '\t'.join(
    ['year', 'count', 'total', 'coverage', 'avg', 'min', '1perc', '10perc',
     '25perc', '50perc', '75perc', '90perc', '99perc', 'max'])
INFO_INDEX = {  # must be consistent with INFO_HEADER
    'coverage': 3,
    '1perc': 6,
    '99perc': 12,
}

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--info_dir', required=True)
  parser.add_argument('--stats_file', required=True)
  args = parser.parse_args()

  features = sorted([feature for feature in os.listdir(args.info_dir)])
  with open(args.stats_file, 'w') as fp:
    print >> fp, '\t'.join(['feature\\stats', 'coverage', '1perc', '99perc'])
    for feature in features:
      info_file = '%s/%s' % (args.info_dir, feature)
      with open(info_file, 'r') as ifp:
        lines = ifp.read().splitlines()
      assert len(lines) > 2
      assert lines[1] == INFO_HEADER
      coverages = []
      perc1s = []
      perc99s = []
      for i in range(2, len(lines)):
        items = lines[i].split('\t')
        coverage = items[INFO_INDEX['coverage']]
        perc1 = items[INFO_INDEX['1perc']]
        perc99 = items[INFO_INDEX['99perc']]
        assert coverage.endswith('%')
        if coverage == '0.00%':
          assert perc1 == '-'
          assert perc99 == '-'
          continue
        coverages.append(float(coverage[:-1]))
        perc1s.append(float(perc1))
        perc99s.append(float(perc99))
      coverage = sum(coverages)/len(coverages)
      perc1 = sum(perc1s)/len(perc1s)
      perc99 = sum(perc99s)/len(perc99s)
      print >> fp, '%s\t%.2f%%\t%.6f\t%.6f' % (
          feature, coverage, perc1, perc99)

if __name__ == '__main__':
  main()

