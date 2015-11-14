#!/usr/bin/python2.7

# Adapted from qd.
""" Gets sector or industry info for stocks.

    Example usage:
      ./get_sector_industry.py --ticker_file=./tickers
                               --info_file=./sf1_ticker_info.txt
                               --sector
                               --output_base_dir=./feature_prep
    or
      ./get_sector_industry.py --ticker_file=./tickers
                               --info_file=./sf1_ticker_info.txt
                               --industry
                               --output_base_dir=./feature_prep

    For each ticker, the sector or industry column is read from the info file,
    and '*\t1' will be written to <output_base_dir>/sector_<ABC>/<ticker>,
    while '*\t0' will be written to the corresponding <ticker> file for all
    other sector folders.

    Sector and industry names are normalized by removing all chars not in
    [A-Za-z].
"""

import argparse
import os
import util

SECTOR_PREFIX = 'sector_'
INDUSTRY_PREFIX = 'industry_'

def normalizeName(name):
  name = ''.join([c for c in name
                   if c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z'])
  if name == '' or name == 'NA' or name == 'None':
    name = 'Unknown'
  return name

def readInfo(info_file, tickers, header):
  raw_dict = util.readSf1Info(info_file, header)
  info_dict = dict()
  names = set()
  for ticker, name in raw_dict.iteritems():
    if ticker not in tickers:
      continue
    info_dict[ticker] = name
    names.add(name)
  for ticker, name in info_dict.iteritems():
    nname = normalizeName(name)
    if nname != name:
      assert nname not in names, (
          'bad normalization: %s => %s' % (name, nname))
    info_dict[ticker] = nname
  return info_dict

def getNameDir(output_base_dir, prefix, name):
  return '%s/%s%s' % (output_base_dir, prefix, name)

def getColumn(ticker_file, info_file, prefix, header, output_base_dir, stats_file):
  tickers = set(util.readTickers(ticker_file))
  info_dict = readInfo(info_file, tickers, header)
  count_dict = {name: 0 for name in info_dict.values()}
  for name in count_dict.iterkeys():
    name_dir = getNameDir(output_base_dir, prefix, name)
    assert not os.path.isdir(name_dir)
    os.mkdir(name_dir)
  for ticker, name in info_dict.iteritems():
    with open('%s/%s' % (getNameDir(output_base_dir, prefix, name), ticker),
              'w') as fp:
      print >> fp, '*\t1'
    for other in count_dict.iterkeys():
      if other == name: continue
      with open('%s/%s' % (getNameDir(output_base_dir, prefix, other), ticker),
                'w') as fp:
        print >> fp, '*\t0'
    count_dict[name] += 1
  with open(stats_file, 'w') as fp:
    for name in sorted(count_dict.keys()):
      print >> fp, '%s: %d' % (name, count_dict[name])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--info_file', required=True)
  parser.add_argument('--sector', action='store_true')
  parser.add_argument('--industry', action='store_true')
  parser.add_argument('--output_base_dir', required=True)
  parser.add_argument('--stats_file', required=True)
  args = parser.parse_args()

  assert args.sector or args.industry, 'must specify --sector or --industry'
  assert not (args.sector and args.industry), (
      'must only specify one of --sector and --industry')

  if args.sector:
    prefix = SECTOR_PREFIX
    header = 'Sector'
  else:
    prefix = INDUSTRY_PREFIX
    header = 'Industry'
  getColumn(args.ticker_file, args.info_file, prefix, header,
            args.output_base_dir, args.stats_file)

if __name__ == '__main__':
  main()

