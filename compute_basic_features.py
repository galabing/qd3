#!/usr/bin/python

# Adapted from qd/scripts/basic_features.py

import argparse
import os
import util

# [indicator, [dimension ...]]
ITEMS = [
    ['ASSETTURNOVER', ['ART']],
    ['CURRENTRATIO', ['ARQ']],
    ['DE', ['ARQ']],
    ['DILUTIONRATIO', ['ARQ', 'ART']],
    ['DIVYIELD', ['ND']],
    ['EBITDAMARGIN', ['ART']],
    ['EPSDILGROWTH1YR', ['ART']],
    ['EPSGROWTH1YR', ['ART']],
    ['EVEBIT', ['ART']],
    ['EVEBITDA', ['ART']],
    ['GROSSMARGIN', ['ART']],
    ['INTERESTBURDEN', ['ART']],
    ['LEVERAGERATIO', ['ART']],
    ['NCFOGROWTH1YR', ['ART']],
    ['NETINCGROWTH1YR', ['ART']],
    ['NETMARGIN', ['ART']],
    ['PE', ['ART']],
    ['PE1', ['ART']],
    ['PS1', ['ART']],
    ['PS', ['ART']],
    ['PB', ['ARQ']],
    ['REVENUEGROWTH1YR', ['ART']],
    ['SHARESWAGROWTH1YR', ['ART']],
    ['PAYOUTRATIO', ['ART']],
    ['ROA', ['ART']],
    ['ROE', ['ART']],
    ['ROS', ['ART']],
    ['TAXEFFICIENCY', ['ART']],
]

def shouldRun(feature_dir, info_file):
  """ Returns whether feature computation should run on the specified dir.
      It should run if: no info file is present, indicating either there
      is no previous run or the previous run has failed.

      Output feature dir is prepared upon output.
  """
  if not os.path.isdir(feature_dir):
    os.mkdir(feature_dir)
  if os.path.isfile(info_file):
    return False
  assert len(os.listdir(feature_dir)) == 0, 'non-empty dir: %s' % feature_dir
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--computer',
      default='/Users/lnyang/lab/qd2/qd2/compute_basic_feature.py')
  parser.add_argument('--processed_dir', required=True,
                      help='dir of processed sf1 data')
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--info_dir', required=True)
  args = parser.parse_args()

  for indicator, dimensions in ITEMS:
    for dimension in dimensions:
      folder = '%s-%s' % (indicator, dimension)
      feature_dir = '%s/%s' % (args.feature_base_dir, folder)
      info_file = '%s/%s' % (args.info_dir, folder)
      if not shouldRun(feature_dir, info_file):
        continue
      cmd = ('%s --processed_dir=%s --ticker_file=%s --dimension=%s '
             '--header=%s --feature_dir=%s --info_file=%s' % (
             args.computer, args.processed_dir, args.ticker_file, dimension,
             indicator, feature_dir, info_file))
      util.run(cmd)

if __name__ == '__main__':
  main()

