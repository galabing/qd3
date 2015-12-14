#!/usr/bin/python2.7

import argparse
import os
import util

# https://docs.google.com/spreadsheets/d/1XwI_qtsYzTwNhEnxPhGf2ftEl0EwXCc_c_1KVS1_w8w/edit#gid=400608303&vpid=A1
# with coverage > 0
# 2015/12/13: + INVCAPAVG-ART ROIC-ART
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
    'INVCAPAVG-ART',
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
    'ROIC-ART',
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

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--computer',
      default='/Users/lnyang/lab/qd2/qd2/compute_hori_perc_feature.py')
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--suffix', required=True)
  parser.add_argument('--group_map_file')
  parser.add_argument('--rank', action='store_true')
  args = parser.parse_args()

  group_map_arg = ''
  if args.group_map_file:
    group_map_arg = '--group_map_file=%s' % args.group_map_file
  rank_arg = ''
  if args.rank:
    rank_arg = '--rank'

  for feature in SF1_ITEMS:
    input_dir = '%s/%s' % (args.feature_base_dir, feature)
    output_dir = '%s/%s%s' % (args.feature_base_dir, feature, args.suffix)
    if not os.path.isdir(output_dir):
      os.mkdir(output_dir)
    cmd = '%s --input_dir=%s --output_dir=%s %s %s' % (
        args.computer, input_dir, output_dir,
        group_map_arg, rank_arg)
    util.run(cmd)

if __name__ == '__main__':
  main()

