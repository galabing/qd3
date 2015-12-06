#!/usr/bin/python2.7

""" Gets sector or industry feature for stocks.

    Example usage:
      ./get_sector_industry_feature.py --map_file=./sector_map
                               --sector
                               --output_base_dir=./feature_prep
    or
      ./get_sector_industry_feature.py --map_file=./industry_map
                               --industry
                               --output_base_dir=./feature_prep

    For each ticker, the sector or industry column is read from the map file,
    and '*\t1' will be written to <output_base_dir>/sector_<ABC>/<ticker>,
    while '*\t0' will be written to the corresponding <ticker> file for all
    other sector folders.
"""

import argparse
import os
import util

SECTOR_PREFIX = 'sector_'
INDUSTRY_PREFIX = 'industry_'

def getNameDir(output_base_dir, prefix, name):
  return '%s/%s%s' % (output_base_dir, prefix, name)

def getFeature(map_file, prefix, output_base_dir):
  with open(map_file, 'r') as fp:
    lines = fp.read().splitlines()
  name_dict = dict()  # ticker => name
  for line in lines:
    ticker, name = line.split('\t')
    name_dict[ticker] = name
  names = set(name_dict.values())
  for name in names:
    name_dir = getNameDir(output_base_dir, prefix, name)
    if not os.path.isdir(name_dir):
      os.mkdir(name_dir)
  for ticker, name in name_dict.iteritems():
    with open('%s/%s' % (getNameDir(output_base_dir, prefix, name), ticker),
              'w') as fp:
      print >> fp, '*\t1'
    for other in names:
      if other == name: continue
      with open('%s/%s' % (getNameDir(output_base_dir, prefix, other), ticker),
                'w') as fp:
        print >> fp, '*\t0'

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--map_file', required=True)
  parser.add_argument('--sector', action='store_true')
  parser.add_argument('--industry', action='store_true')
  parser.add_argument('--output_base_dir', required=True)
  args = parser.parse_args()

  assert args.sector or args.industry, 'must specify --sector or --industry'
  assert not (args.sector and args.industry), (
      'must only specify one of --sector and --industry')

  if args.sector:
    prefix = SECTOR_PREFIX
  else:
    prefix = INDUSTRY_PREFIX
  getFeature(args.map_file, prefix, args.output_base_dir)

if __name__ == '__main__':
  main()

