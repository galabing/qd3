#!/usr/bin/python2.7

# Adapted from qd/scripts/basic_features.py

import argparse
import os
import util

# [indicator, [dimension ...]]
ITEMS = [
    # income
    ['REVENUE', ['ARQ', 'ART']],
    ['COR', ['ARQ', 'ART']],
    ['GP', ['ARQ', 'ART']],
    ['RND', ['ARQ', 'ART']],
    ['SGNA', ['ARQ', 'ART']],
    ['EBIT', ['ARQ', 'ART']],
    ['INTEXP', ['ARQ', 'ART']],
    ['EBT', ['ARQ', 'ART']],
    ['TAXEXP', ['ARQ', 'ART']],
    ['NETINC', ['ARQ', 'ART']],
    ['PREFDIVIS', ['ARQ', 'ART']],
    ['NETINCCMN', ['ARQ', 'ART']],
    ['NETINCDIS', ['ARQ', 'ART']],
    ['EPS', ['ARQ', 'ART']],
    ['EPSDIL', ['ARQ', 'ART']],
    ['SHARESWA', ['ARQ', 'ART']],
    ['SHARESWADIL', ['ARQ', 'ART']],
    ['DPS', ['ARQ', 'ART']],
    # cash flow
    ['NCFO', ['ARQ', 'ART']],
    ['DEPAMOR', ['ARQ', 'ART']],
    ['NCFI', ['ARQ', 'ART']],
    ['CAPEX', ['ARQ', 'ART']],
    ['NCFF', ['ARQ', 'ART']],
    ['NCFDEBT', ['ARQ', 'ART']],
    ['NCFCOMMON', ['ARQ', 'ART']],
    ['NCFDIV', ['ARQ', 'ART']],
    ['NCFX', ['ARQ', 'ART']],
    ['NCF', ['ARQ', 'ART']],
    # balance
    ['ASSETS', ['ARQ']],
    ['ASSETSC', ['ARQ']],
    ['ASSETSNC', ['ARQ']],
    ['CASHNEQ', ['ARQ']],
    ['RECEIVABLES', ['ARQ']],
    ['INTANGIBLES', ['ARQ']],
    ['INVENTORY', ['ARQ']],
    ['LIABILITIES', ['ARQ']],
    ['LIABILITIESC', ['ARQ']],
    ['LIABILITIESNC', ['ARQ']],
    ['DEBT', ['ARQ']],
    ['PAYABLES', ['ARQ']],
    ['EQUITY', ['ARQ']],
    ['RETEARN', ['ARQ']],
    ['ACCOCI', ['ARQ']],
    # metrics
    ['ASSETTURNOVER', ['ART']],
    ['ASSETSAVG', ['ART']],
    ['BVPS', ['ARQ']],
    ['CURRENTRATIO', ['ARQ']],
    ['DE', ['ARQ']],
    ['DILUTIONRATIO', ['ARQ', 'ART']],
    ['DIVYIELD', ['ND']],
    ['EBITDA', ['ARQ', 'ART']],
    ['EBITDAMARGIN', ['ART']],
    ['EPSDILGROWTH1YR', ['ART']],
    ['EPSGROWTH1YR', ['ART']],
    ['EQUITYAVG', ['ART']],
    ['EV', ['ND']],
    ['EVEBIT', ['ART']],
    ['EVEBITDA', ['ART']],
    ['FCF', ['ARQ', 'ART']],
    ['FCFPS', ['ARQ', 'ART']],
    ['GROSSMARGIN', ['ART']],
    ['INTERESTBURDEN', ['ART']],
    ['INVCAP', ['ARQ']],
    ['INVCAPAVG', ['ART']],
    ['LEVERAGERATIO', ['ART']],
    ['MARKETCAP', ['ND']],
    ['NCFOGROWTH1YR', ['ART']],
    ['NETINCGROWTH1YR', ['ART']],
    ['NETMARGIN', ['ART']],
    ['PE', ['ART']],
    ['PE1', ['ART']],
    ['PS1', ['ART']],
    ['PS', ['ART']],
    ['PB', ['ARQ']],
    ['REVENUEGROWTH1YR', ['ART']],
    ['ROIC', ['ART']],
    ['SHARESWAGROWTH1YR', ['ART']],
    ['SPS', ['ART']],
    ['PAYOUTRATIO', ['ART']],
    ['ROA', ['ART']],
    ['ROE', ['ART']],
    ['ROS', ['ART']],
    ['TANGIBLES', ['ARQ']],
    ['TAXEFFICIENCY', ['ART']],
    ['TBVPS', ['ARQ']],
    ['WORKINGCAPITAL', ['ARQ']],
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

