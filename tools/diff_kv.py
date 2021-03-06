#!/usr/bin/python2.7

""" Diffs key-value files (eg, yahoo price data) between two directories.
    This is used to compare snapshots of data and ensure consistency.

    Example usage:
      ./diff_kv.py --src_dir=./old/price
                   --dst_dir=./new/price
                   --output_file=./diff-summary
"""

import argparse
import os

EPS = 0.01

def readKeyValueDict(kv_file):
  with open(kv_file, 'r') as fp:
    lines = fp.read().splitlines()
  kv = dict()
  for line in lines:
    k, v = line.split('\t')
    assert k not in kv, 'dup key %s in %s' % (k, kv_file)
    kv[k] = float(v)
  return kv

def diff(args):
  fp = open(args.output_file, 'w')

  src_tickers = set(os.listdir(args.src_dir))
  dst_tickers = set(os.listdir(args.dst_dir))
  print '%d tickers in src' % len(src_tickers)
  print '%d tickers in dst' % len(dst_tickers)

  print >> fp, 'src (%s): %d tickers' % (args.src_dir, len(src_tickers))
  print >> fp, 'dst (%s): %d tickers' % (args.dst_dir, len(dst_tickers))
  delta = src_tickers - dst_tickers
  print '%d tickers in src but not dst' % len(delta)
  print >> fp, 'tickers in src but not dst: %s' % (delta)
  delta = dst_tickers - src_tickers
  print '%d tickers in dst but not src' % len(delta)
  print >> fp, 'tickers in dst but not src: %s' % (delta)

  tickers = sorted(src_tickers & dst_tickers)
  errors = []
  for ticker in tickers:
    has_error = False

    src_kv = readKeyValueDict('%s/%s' % (args.src_dir, ticker))
    dst_kv = readKeyValueDict('%s/%s' % (args.dst_dir, ticker))
    src_keys = set(src_kv.keys())
    dst_keys = set(dst_kv.keys())

    delta = src_keys - dst_keys
    if len(delta) > 0:
      has_error = True
      print >> fp, '[ERROR] key in src but not dst for %s: %s' % (ticker, sorted(delta))
    delta = dst_keys - src_keys
    if len(delta) > 0:
      print >> fp, '[WARNING] key in dst but not src for %s: %s' % (ticker, sorted(delta))

    keys = sorted(src_keys & dst_keys)
    for key in keys:
      src_value = src_kv[key]
      dst_value = dst_kv[key]
      delta = abs(src_value - dst_value)
      if delta > EPS:
        has_error = True
        print >> fp, '[ERROR] value changed for key %s for %s: %f => %f' % (
            key, ticker, src_value, dst_value)

    if has_error:
      errors.append(ticker)
  print '%d tickers have errors: %s' % (len(errors), errors)

  fp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--src_dir', required=True)
  parser.add_argument('--dst_dir', required=True)
  parser.add_argument('--output_file', required=True)
  diff(parser.parse_args())

if __name__ == '__main__':
  main()

