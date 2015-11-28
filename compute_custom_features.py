#!/usr/bin/python2.7

import argparse
import os
import util

# [target, equation]
# https://docs.google.com/document/d/1ej5c3RGpVU9xdGpNkfN2hYnAjCO1ug9i5FfecQi9V2o/edit
ITEMS = [
    ['FCF_REVENUE-ARQ', '{FCF-ARQ}/{REVENUE-ARQ}'],
    ['FCF_REVENUE-ART', '{FCF-ART}/{REVENUE-ART}'],
    ['RECEIVABLES_REVENUE-ARQ', '{RECEIVABLES-ARQ}/{REVENUE-ARQ}'],
    ['COR_INVENTORY-ARQ', '{COR-ARQ}/{INVENTORY-ARQ}'],
    ['INTANGIBLES_ASSETS-ARQ', '{INTANGIBLES-ARQ}/{ASSETS-ARQ}'],
    ['LIABILITIESC_ASSETSC-ARQ', '{LIABILITIESC-ARQ}/{ASSETSC-ARQ}'],
    ['SGNA_REVENUE-ARQ', '{SGNA-ARQ}/{REVENUE-ARQ}'],
    ['SGNA_REVENUE-ART', '{SGNA-ART}/{REVENUE-ART}'],
    ['EBIT_REVENUE-ARQ', '{EBIT-ARQ}/{REVENUE-ARQ}'],
    ['EBIT_REVENUE-ART', '{EBIT-ART}/{REVENUE-ART}'],
    ['EBIT_INTEXP-ARQ', '{EBIT-ARQ}/{INTEXP-ARQ}'],
    ['EBIT_INTEXP-ART', '{EBIT-ART}/{INTEXP-ART}'],
    ['TAXRATE-ARQ', '({EBT-ARQ} - {NETINC-ARQ}) / {NETINC-ARQ}'],
    ['TAXRATE-ART', '({EBT-ART} - {NETINC-ART}) / {NETINC-ART}'],
    ['ASSETS_EQUITY-ARQ', '{ASSETS-ARQ}/{EQUITY-ARQ}'],
    ['QUICKRATIO-ARQ', '({ASSETSC-ARQ} - {INVENTORY-ARQ}) / {LIABILITIESC-ARQ}'],
    ['CASHNEQ_ASSETS-ARQ', '{CASHNEQ-ARQ}/{ASSETS-ARQ}'],
]

def shouldRun(feature_base_dir, info_dir, target):
  """ Returns whether feature computation should run on the specified dir.
      It should run if: no info file is present, indicating either there
      is no previous run or the previous run has failed.

      Output feature dir is prepared upon output.
  """
  target_dir = '%s/%s' % (feature_base_dir, target)
  if not os.path.isdir(target_dir):
    os.mkdir(target_dir)
  if os.path.isfile('%s/%s' % (info_dir, target)):
    return False
  assert len(os.listdir(target_dir)) == 0, 'non-empty dir: %s' % target_dir
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--computer',
      default='/Users/lnyang/lab/qd2/qd2/compute_custom_feature.py')
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--info_dir', required=True)
  args = parser.parse_args()

  for target, formula in ITEMS:
    if not shouldRun(args.feature_base_dir, args.info_dir, target):
      continue
    cmd = ('%s --feature_base_dir=%s --ticker_file=%s --info_base_dir=%s '
           '--equation="{%s} = %s"' % (
           args.computer, args.feature_base_dir, args.ticker_file,
           args.info_dir, target, formula))
    util.run(cmd)

if __name__ == '__main__':
  main()

