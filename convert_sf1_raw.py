#!/usr/bin/python2.7

# Adapted from qd.
""" Converts unzipped file of entire SF1 database into a set of raw files.

    Usage:
      ./convert_sf1_raw.py --sf1_file=SF1_20150502.csv
                           --indicator_file=./indicators.txt
                           --raw_dir=./raw

    It does one pass through sf1_file and separates lines of different
    tickers into different output raw files.  The raw files of each ticker
    should be small enough to be loaded into memory for further processing.
"""

import argparse
import datetime
import os

# If this is modified readIndicatorMeta() also needs to be modified!
INDICATOR_HEADER = '\t'.join(['Indicator',
                              'Title',
                              'Available Dimensions',
                              'Statement',
                              'Description',
                              'NA Value'])

def readIndicatorMeta(indicator_file):
  with open(indicator_file, 'r') as fp:
    lines = fp.read().splitlines()

  indicator_meta = dict()
  assert len(lines) > 0
  assert lines[0] == INDICATOR_HEADER
  for i in range(1, len(lines)):
    indicator, title, dimensions, statement, description, na = (
        lines[i].split('\t'))
    dimensions = [d for d in dimensions.split(',') if d != '']
    assert indicator not in indicator_meta
    indicator_meta[indicator] = set(dimensions)

  return indicator_meta

def processLine(line, indicator_meta):
  """ Processes one line from sf1_file, sanity-checks data, and returns
      ticker and line of output.
  """
  # Eg, AA_ACCOCI_ARQ,2004-02-27,-569000000.0
  assert line[-1] == '\n'
  line = line[:-1]
  label, date, value = line.split(',')
  # Check label.
  items = label.split('_')
  assert len(items) == 2 or len(items) == 3
  ticker, indicator = items[0], items[1]
  assert indicator in indicator_meta, (
      'unsupported indicator %s for ticker %s' % (indicator, ticker))
  if len(items) == 2:
    assert len(indicator_meta[indicator]) == 0, (
        'unsupported dimension for (%s, %s): None (supported: %s)' % (
            ticker, indicator, indicator_meta[indicator]))
  else:
    assert items[2] in indicator_meta[indicator], (
        'unsupported dimension for (%s, %s): %s (supported: %s)' % (
            ticker, indicator, items[2], indicator_meta[indicator]))
  # Check date.
  try:
    tmp_date = datetime.datetime.strptime(date, '%Y-%m-%d')
  except ValueError:
    assert False, 'unsupported date format in line: %s' % line
  # Check value.
  try:
    tmp_value = float(value)
  except ValueError:
    assert False, 'unsupported value format in line: %s' % line

  return ticker, line

def convertSf1Raw(sf1_file, indicator_file, raw_dir, max_lines=0):
  # Since we always append to raw files (lines of a ticker may not be
  # adjacent in sf1_file) it's only sane to run this script with an
  # empty raw_dir.
  assert len(os.listdir(raw_dir)) == 0, (
      'nonempty raw dir: %s' % raw_dir)

  # Read indicator metadata for sanity-checking sf1_file.
  indicator_meta = readIndicatorMeta(indicator_file)

  num_lines = 0
  output_ticker = None
  output_fp = None

  with open(sf1_file, 'r') as fp:
    while True:
      line = fp.readline()
      if line == '':
        break
      # Prepare output data.
      ticker, line = processLine(line, indicator_meta)
      # Prepare output fp.
      if ticker != output_ticker:
        if output_fp is not None:
          output_fp.close()
        output_fp = open('%s/%s' % (raw_dir, ticker), 'a')
        output_ticker = ticker
      print >> output_fp, line

      num_lines += 1
      if max_lines > 0 and num_lines >= max_lines:
        break
  if output_fp is not None:
    output_fp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--sf1_file', required=True,
                      help='unzipped file of entire SF! database from quandl')
  parser.add_argument('--indicator_file', required=True,
                      help='file of supported indicators in SF1')
  parser.add_argument('--raw_dir', required=True,
                      help='output dir of raw files')
  parser.add_argument('--max_lines', type=int, default=0,
                      help='max number of lines to process from sf1_file; '
                           'only use this for debugging')
  args = parser.parse_args()
  convertSf1Raw(args.sf1_file, args.indicator_file, args.raw_dir,
                args.max_lines)

if __name__ == '__main__':
  main()

