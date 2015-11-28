#!/usr/bin/python2.7

import argparse
import os
import util

# https://docs.google.com/spreadsheets/d/1XwI_qtsYzTwNhEnxPhGf2ftEl0EwXCc_c_1KVS1_w8w/edit#gid=400608303&vpid=A1
# with coverage > 0
SF1_ITEMS = [
    'ACCOCI-ARQ',
    'ASSETS-ARQ',
    'ASSETSAVG-ART',
    'ASSETSC-ARQ',
    'ASSETSNC-ARQ',
    'ASSETS_EQUITY-ARQ',
    'ASSETTURNOVER-ART',
    'BVPS-ARQ',
    'CAPEX-ARQ',
    'CAPEX-ART',
    'CASHNEQ-ARQ',
    'CASHNEQ_ASSETS-ARQ',
    'COR-ARQ',
    'COR-ART',
    'CURRENTRATIO-ARQ',
    'DE-ARQ',
    'DEBT-ARQ',
    'DEPAMOR-ARQ',
    'DEPAMOR-ART',
    'DILUTIONRATIO-ARQ',
    'DILUTIONRATIO-ART',
    'DIVYIELD-ND',
    'DPS-ARQ',
    'DPS-ART',
    'EBIT-ARQ',
    'EBIT-ART',
    'EBITDA-ARQ',
    'EBITDA-ART',
    'EBITDAMARGIN-ART',
    'EBIT_INTEXP-ARQ',
    'EBIT_INTEXP-ART',
    'EBIT_REVENUE-ARQ',
    'EBIT_REVENUE-ART',
    'EBT-ARQ',
    'EBT-ART',
    'EPS-ARQ',
    'EPS-ART',
    'EPSDIL-ARQ',
    'EPSDIL-ART',
    'EPSDILGROWTH1YR-ART',
    'EPSGROWTH1YR-ART',
    'EQUITY-ARQ',
    'EQUITYAVG-ART',
    'EV-ND',
    'EVEBIT-ART',
    'EVEBITDA-ART',
    'FCF-ARQ',
    'FCF-ART',
    'FCFPS-ARQ',
    'FCFPS-ART',
    'FCF_REVENUE-ARQ',
    'FCF_REVENUE-ART',
    'GP-ARQ',
    'GP-ART',
    'GROSSMARGIN-ART',
    'INTANGIBLES-ARQ',
    'INTANGIBLES_ASSETS-ARQ',
    'INTERESTBURDEN-ART',
    'INTEXP-ARQ',
    'INTEXP-ART',
    'LEVERAGERATIO-ART',
    'LIABILITIES-ARQ',
    'LIABILITIESC-ARQ',
    'LIABILITIESC_ASSETSC-ARQ',
    'LIABILITIESNC-ARQ',
    'MARKETCAP-ND',
    'NCF-ARQ',
    'NCF-ART',
    'NCFF-ARQ',
    'NCFF-ART',
    'NCFI-ARQ',
    'NCFI-ART',
    'NCFO-ARQ',
    'NCFO-ART',
    'NCFOGROWTH1YR-ART',
    'NCFX-ARQ',
    'NCFX-ART',
    'NETINC-ARQ',
    'NETINC-ART',
    'NETINCCMN-ARQ',
    'NETINCCMN-ART',
    'NETINCDIS-ARQ',
    'NETINCDIS-ART',
    'NETINCGROWTH1YR-ART',
    'NETMARGIN-ART',
    'PAYABLES-ARQ',
    'PAYOUTRATIO-ART',
    'PB-ARQ',
    'PE-ART',
    'PE1-ART',
    'PREFDIVIS-ARQ',
    'PREFDIVIS-ART',
    'PS-ART',
    'PS1-ART',
    'RECEIVABLES-ARQ',
    'RECEIVABLES_REVENUE-ARQ',
    'REVENUE-ARQ',
    'REVENUE-ART',
    'REVENUEGROWTH1YR-ART',
    'RND-ARQ',
    'RND-ART',
    'ROA-ART',
    'ROE-ART',
    'ROS-ART',
    'SGNA-ARQ',
    'SGNA-ART',
    'SGNA_REVENUE-ARQ',
    'SGNA_REVENUE-ART',
    'SHARESWA-ARQ',
    'SHARESWA-ART',
    'SHARESWADIL-ARQ',
    'SHARESWADIL-ART',
    'SHARESWAGROWTH1YR-ART',
    'SPS-ART',
    'TANGIBLES-ARQ',
    'TAXEFFICIENCY-ART',
    'TAXEXP-ARQ',
    'TAXEXP-ART',
    'TAXRATE-ARQ',
    'TAXRATE-ART',
    'TBVPS-ARQ',
    'WORKINGCAPITAL-ARQ',
]
SF1_WINDOWS = '0,1,2,3,4,8,16'

PRICE_ITEMS = ['adjprice']
PRICE_WINDOWS = '0,1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48'

def shouldRun(output_dir, info_dir, feature, windows):
  """ Returns whether feature computation should run on the specified dir.
      It should run if: no info file is present, indicating either there
      is no previous run or the previous run has failed.

      Output feature dir is prepared upon output.
  """
  windows = [int(w) for w in windows.split(',')]
  missing_info = False
  for window in windows:
    target_file = '%s_hp-%d' % (feature, window)
    if not os.path.isfile('%s/%s' % (info_dir, target_file)):
      missing_file = True
      target_dir = '%s/%s' % (output_dir, target_file)
      if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
      else:
        assert len(os.listdir(target_dir)) == 0, 'non-empty dir: %s' % target_dir
  return missing_info

def maybeRun(args, input_dir, feature, windows):
  if not shouldRun(args.feature_base_dir, args.info_dir, feature, windows):
    return
  cmd = ('%s --input_dir=%s --output_dir=%s --feature=%s --windows=%s '
         '--ticker_file=%s --info_base_dir=%s' % (
         args.computer, input_dir, args.feature_base_dir, feature, windows,
         args.ticker_file, args.info_dir))
  util.run(cmd)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--computer',
      default='/Users/lnyang/lab/qd2/qd2/compute_vert_perc_feature.py')
  parser.add_argument('--sf1_input_dir', required=True)
  parser.add_argument('--price_input_dir', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--info_dir', required=True)
  args = parser.parse_args()

  for feature in SF1_ITEMS:
    maybeRun(args, args.sf1_input_dir, feature, SF1_WINDOWS)
  for feature in PRICE_ITEMS:
    maybeRun(args, args.price_input_dir, feature, PRICE_WINDOWS)

if __name__ == '__main__':
  main()

