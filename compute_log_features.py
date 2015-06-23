#!/usr/bin/python2.7

# Adapted from qd/scripts/log_features.py
# TODO: combine this with compute_basic_features.py;
#       most flags are the same (except this one has --negate).

import argparse
import os
import util

# [indicator, negate, [dimension ...]]
ITEMS = [
    # income
    ['REVENUE', False, ['ARQ', 'ART']],
    ['COR', False, ['ARQ', 'ART']],
    ['GP', False, ['ARQ', 'ART']],
    ['RND', False, ['ARQ', 'ART']],
    ['SGNA', False, ['ARQ', 'ART']],
    ['EBIT', False, ['ARQ', 'ART']],
    ['INTEXP', False, ['ARQ', 'ART']],
    ['EBT', False, ['ARQ', 'ART']],
    ['TAXEXP', False, ['ARQ', 'ART']],
    ['NETINC', False, ['ARQ', 'ART']],
    ['PREFDIVIS', False, ['ARQ', 'ART']],
    ['NETINCCMN', False, ['ARQ', 'ART']],
    ['NETINCDIS', False, ['ARQ', 'ART']],
    # cash flow
    ['NCFO', False, ['ARQ', 'ART']],
    ['DEPAMOR', False, ['ARQ', 'ART']],
    ['NCFI', False, ['ARQ', 'ART']],
    ['CAPEX', True, ['ARQ', 'ART']],  # negate
    ['NCFF', False, ['ARQ', 'ART']],
    ['NCFX', False, ['ARQ', 'ART']],
    ['NCF', False, ['ARQ', 'ART']],
    # balance
    ['ASSETS', False, ['ARQ']],
    ['ASSETSC', False, ['ARQ']],
    ['ASSETSNC', False, ['ARQ']],
    ['CASHNEQ', False, ['ARQ']],
    ['RECEIVABLES', False, ['ARQ']],
    ['INTANGIBLES', False, ['ARQ']],
    ['LIABILITIES', False, ['ARQ']],
    ['LIABILITIESC', False, ['ARQ']],
    ['LIABILITIESNC', False, ['ARQ']],
    ['DEBT', False, ['ARQ']],
    ['PAYABLES', False, ['ARQ']],
    ['EQUITY', False, ['ARQ']],
    ['ACCOCI', False, ['ARQ']],
    # metrics
    ['ASSETSAVG', False, ['ART']],
    ['EBITDA', False, ['ARQ', 'ART']],
    ['EQUITYAVG', False, ['ART']],
    ['EV', False, ['ND']],
    ['FCF', False, ['ARQ', 'ART']],
    ['MARKETCAP', False, ['ND']],
    ['TANGIBLES', False, ['ARQ']],
    ['WORKINGCAPITAL', False, ['ARQ']],
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
      default='/Users/lnyang/lab/qd2/qd2/compute_log_feature.py')
  parser.add_argument('--processed_dir', required=True,
                      help='dir of processed sf1 data')
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--info_dir', required=True)
  args = parser.parse_args()

  for indicator, negate, dimensions in ITEMS:
    for dimension in dimensions:
      negate_str = ''
      negate_flag = ''
      if negate:
        negate_str = '-'
        negate_flag = '--negate'
      folder = 'log%s%s-%s' % (negate_str, indicator, dimension)
      feature_dir = '%s/%s' % (args.feature_base_dir, folder)
      info_file = '%s/%s' % (args.info_dir, folder)
      if not shouldRun(feature_dir, info_file):
        continue
      cmd = ('%s --processed_dir=%s --ticker_file=%s --dimension=%s '
             '--header=%s --feature_dir=%s --info_file=%s %s' % (
             args.computer, args.processed_dir, args.ticker_file, dimension,
             indicator, feature_dir, info_file, negate_flag))
      util.run(cmd)

if __name__ == '__main__':
  main()

