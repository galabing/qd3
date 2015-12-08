#!/usr/bin/python2.7

""" Computes Pearson coeff for features.

    Example usage:
      ./compute_pearson.py --data_file=./data
                           --feature_file=./feature_list
                           --meta_file=./meta
                           --min_price=5
                           --max_price=10
                           --price_dir=./price
                           --min_volatility=0.25
                           --max_volatility=0.5
                           --volatility_dir=./volatility
                           --min_pos=0.1
                           --max_neg=-0.1
                           --output_file=./output.tsv
                           --group_output_file=./group_output.tsv

    It filters on data by
    --min_price (--price_dir also required)
    --max_volatility (--volatility_dir also required)
    and --min_pos/--max_neg to create corresponding 1/0 labels,
    computes Pearson coeff for each feature against labels,
    and writes output to --output_file:
      <feature> <pearson> <p-value>

    If --group_output_file is set, features are grouped by their
    prefix (before _) and Pearson coeff is computed within each group.
      <prefix> <feature1> <feature2> <pearson> <p-value>
"""

from numpy import loadtxt
from scipy.stats import pearsonr
from sklearn.preprocessing import Imputer
import argparse

MIN_VALUE = float('-Inf')
MAX_VALUE = float('Inf')

TMP_DATA_FILE = '/tmp/pearson_data'
TMP_LABEL_FILE = '/tmp/pearson_label'

MAX_GROUP_SIZE = 10

def readKeyValueDict(kv_file):
  with open(kv_file, 'r') as fp:
    lines = fp.read().splitlines()
  kv = dict()
  for line in lines:
    k, v = line.split('\t')
    assert k not in kv, 'dup key %s in %s' % (k, kv_file)
    kv[k] = float(v)
  return kv

def filter(args):
  counter = {
      'between_neg_pos': 0,
      'min_price': 0,
      'max_price': 0,
      'min_volatility': 0,
      'max_volatility': 0,
      'selected': 0,
  }

  ifps = {
      'data': open(args.data_file, 'r'),
      'meta': open(args.meta_file, 'r'),
  }
  ofps = {
      'data': open(TMP_DATA_FILE, 'w'),
      'label': open(TMP_LABEL_FILE, 'w'),
  }

  use_price = (args.min_price != MIN_VALUE or args.max_price != MAX_VALUE)
  use_volatility = (args.min_volatility != MIN_VALUE or args.max_volatility != MAX_VALUE)

  prev_ticker = None
  prices = None
  volatilities = None

  while True:
    data_line = ifps['data'].readline()
    meta_line = ifps['meta'].readline()
    if data_line == '':
      assert meta_line == '', 'inconsistent line count between data/meta'
      break
    assert data_line.endswith('\n')
    assert meta_line.endswith('\n')
    data_line = data_line[:-1]
    meta_line = meta_line[:-1]

    ticker, date, _, gain = meta_line.split('\t')
    if ticker != prev_ticker:
      prev_ticker = ticker
      if use_price:
        prices = readKeyValueDict('%s/%s' % (args.price_dir, ticker))
      if use_volatility:
        volatilities = readKeyValueDict('%s/%s' % (args.volatility_dir, ticker))

    gain = float(gain)
    label = None
    if gain >= args.min_pos:
      label = 1.0
    elif gain <= args.max_neg:
      label = 0.0
    if label is None:
      counter['between_neg_pos'] += 1
      continue

    if prices is not None:
      price = prices[date]
      if price < args.min_price:
        counter['min_price'] += 1
        continue
      if price > args.max_price:
        counter['max_price'] += 1
        continue

    if volatilities is not None:
      volatility = volatilities[date]
      if volatility < args.min_volatility:
        counter['min_volatility'] += 1
        continue
      if volatility > args.max_volatility:
        counter['max_volatility'] += 1
        continue

    counter['selected'] += 1
    print >> ofps['data'], data_line
    print >> ofps['label'], '%f' % label

  for fp in ifps.itervalues():
    fp.close()
  for fp in ofps.itervalues():
    fp.close()

  print counter

def getGroups(features):
  groups = dict()  # prefix => [features]
  for feature in features:
    p = feature.find('_hp')
    if p < 0:
      prefix = feature
    else:
      prefix = feature[:p]
    if prefix not in groups:
      groups[prefix] = [feature]
    else:
      groups[prefix].append(feature)
  return groups

def computePearson(args):
  filter(args)

  with open(args.feature_file, 'r') as fp:
    features = [line for line in fp.read().splitlines()
                if not line.startswith('#')]

  X = loadtxt(TMP_DATA_FILE)
  y = loadtxt(TMP_LABEL_FILE)

  assert X.shape[0] == y.shape[0]
  assert X.shape[1] == len(features)

  imputer = Imputer(strategy='median', copy=False)
  X = imputer.fit_transform(X)

  if args.output_file:
    with open(args.output_file, 'w') as fp:
      print >> fp, '\t'.join(['feature', 'coeff', 'pvalue'])
      for i in range(len(features)):
        coeff, pvalue = pearsonr(X[:, i], y)
        print >> fp, '%s\t%f\t%f' % (features[i], coeff, pvalue)

  if args.group_output_file:
    groups = getGroups(features)
    index = {features[i]: i for i in range(len(features))}
    with open(args.group_output_file, 'w') as fp:
      print >> fp, '\t'.join(['prefix', 'feature1', 'feature2', 'coeff', 'pvalue'])
      for prefix, group in groups.iteritems():
        for i in range(len(group)):
          for j in range(i+1, len(group)):
            coeff, pvalue = pearsonr(X[:, index[group[i]]], X[:, index[group[j]]])
            print >> fp, '%s\t%s\t%s\t%f\t%f' % (
                prefix, group[i], group[j], coeff, pvalue)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_file', required=True)
  parser.add_argument('--feature_file', required=True)
  parser.add_argument('--meta_file', required=True)
  parser.add_argument('--min_price', type=float, default=MIN_VALUE)
  parser.add_argument('--max_price', type=float, default=MAX_VALUE)
  parser.add_argument('--price_dir')
  parser.add_argument('--min_volatility', type=float, default=MIN_VALUE)
  parser.add_argument('--max_volatility', type=float, default=MAX_VALUE)
  parser.add_argument('--volatility_dir')
  parser.add_argument('--min_pos', type=float, default=0)
  parser.add_argument('--max_neg', type=float, default=0)
  parser.add_argument('--output_file')
  parser.add_argument('--group_output_file')
  args = parser.parse_args()

  # Sanity checks on args.
  if args.min_price != MIN_VALUE or args.max_price != MAX_VALUE:
    assert args.price_dir, 'must specify --price_dir if --min_price/--max_price is set'
  if args.min_volatility != MIN_VALUE or args.max_volatility != MAX_VALUE:
    assert args.volatility_dir, 'must specify --volatility_dir if --min_volatility/--max_volatility is set'
  assert args.output_file or args.group_output_file, (
    'must at least specify one of --output_file and --group_output_file')

  computePearson(args)

if __name__ == '__main__':
  main()

