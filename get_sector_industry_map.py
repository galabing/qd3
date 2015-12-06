#!/usr/bin/python2.7

""" Gets sector or industry info for stocks.

    Example usage:
      ./get_sector_industry_map.py --ticker_file=./tickers
                               --info_file=./sf1_ticker_info.txt
                               --sector
                               --map_file=./sector_map
                               --stats_file=./sector_stats
    or
      ./get_sector_industry_map.py --ticker_file=./tickers
                               --info_file=./sf1_ticker_info.txt
                               --industry
                               --map_file=./industry_map
                               --stats_file=./industry_stats

    Sector and industry names are normalized by removing all chars not in
    [A-Za-z].
"""

import argparse
import os
import util

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

def getColumn(ticker_file, info_file, header, map_file, stats_file):
  tickers = set(util.readTickers(ticker_file))
  info_dict = readInfo(info_file, tickers, header)
  count_dict = {name: 0 for name in info_dict.values()}
  with open(map_file, 'w') as fp:
    for ticker in sorted(tickers):
      name = info_dict[ticker]
      print >> fp, '%s\t%s' % (ticker, name)
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
  parser.add_argument('--map_file', required=True)
  parser.add_argument('--stats_file', required=True)
  args = parser.parse_args()

  assert args.sector or args.industry, 'must specify --sector or --industry'
  assert not (args.sector and args.industry), (
      'must only specify one of --sector and --industry')

  if args.sector:
    header = 'Sector'
  else:
    header = 'Industry'
  getColumn(args.ticker_file, args.info_file, header,
            args.map_file, args.stats_file)

if __name__ == '__main__':
  main()

