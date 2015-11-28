#!/usr/bin/python2.7

""" Computes custom feature from simple equations.

    Example usage:
      ./compute_custom_feature.py --feature_base_dir=./features
                                  --equation="{TAXRATE-ART} = ({EBT-ART} - {NETINC-ART}) / {NETINC-ART}"
                                  --ticker_file=./tickers
                                  --info_base_dir=./info
"""

import argparse
import logging
import os
import re
import util

def findSymbols(equation):
  target, formula = equation.split('=')
  target = target.strip()
  assert target.startswith('{') and target.endswith('}'), (
      'bad equation: %s' % equation)
  target = target[1:-1]
  formula = formula.strip()

  symbols = set()
  index = 0
  while index < len(formula):
    p = formula.find('{', index)
    if p < 0:
      break
    q = formula.find('}', p)
    assert q > p, 'bad equation: %s' % equation
    symbols.add(formula[p+1:q])
    index = q + 1
  assert len(symbols) > 0, 'bad equation: %s'
  return target, symbols, formula

def computeCustomFeature(feature_dir, equation, ticker_file, info_dir):
  target, symbols, formula = findSymbols(equation)
  for symbol in symbols:
    assert os.path.isdir('%s/%s' % (feature_dir, symbol)), (
        'nonexistent symbol: %s' % symbol)
  target_dir = '%s/%s' % (feature_dir, target)
  if not os.path.isdir(target_dir):
    os.mkdir(target_dir)
  pattern = re.compile("|".join([re.escape('{%s}' % symbol) for symbol in symbols]))

  tickers = util.readTickers(ticker_file)
  feature_info = []  # [[yyyy, feature] ...]
  stats = {'missing_symbol': 0, 'missing_date': 0, 'divide_by_zero': 0}
  for ticker in tickers:
    missing_symbol = False
    for symbol in symbols:
      if not os.path.isfile('%s/%s/%s' % (feature_dir, symbol, ticker)):
        missing_symbol = True
        break
    if missing_symbol:
      stats['missing_symbol'] += 1
      continue
    data = {symbol: util.readKeyValueDict('%s/%s/%s' % (feature_dir, symbol, ticker))
            for symbol in symbols}
    dates = None
    for symbol, dfeatures in data.iteritems():
      if dates is None:
        dates = set(dfeatures.keys())
      else:
        dates |= set(dfeatures.keys())
    with open('%s/%s' % (target_dir, ticker), 'w') as fp:
      for date in sorted(dates):
        year = util.ymdToY(date)
        missing_date = False
        for symbol in symbols:
          if date not in data[symbol]:
            missing_date = True
            break
        if missing_date:
          stats['missing_date'] += 1
          feature_info.append((year, None))
          continue
        replace = {re.escape('{%s}' % symbol): '%f' % data[symbol][date] for symbol in symbols}
        rformula = pattern.sub(lambda m: replace[re.escape(m.group(0))], formula)
        try:
          feature = eval(rformula)
        except ZeroDivisionError:
          stats['divide_by_zero'] += 1
          feature_info.append((year, None))
          continue
        print >> fp, '%s\t%f' % (date, feature)
        feature_info.append((year, feature))
  util.writeFeatureInfo(
      [feature_dir, equation, ticker_file],
      feature_info, '%s/%s' % (info_dir, target))
  logging.info('stats: %s' % stats)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--feature_base_dir', required=True)
  parser.add_argument('--equation', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--info_base_dir', required=True)
  args = parser.parse_args()
  computeCustomFeature(args.feature_base_dir, args.equation, args.ticker_file,
                       args.info_base_dir)

if __name__ == '__main__':
  main()

