#!/usr/bin/python

# Adapted from qd.
""" Converts unzipped file of entire EOD database into a set of raw files.

    Usage:
      ./convert_eod_raw.py --eod_file=./EOD_20150505.csv
                           --raw_dir=./raw

    It does one pass through eod_file and separates lines of different
    tickers into different output raw files.  The raw files of each ticker
    should be small enough to be loaded into memory for further processing.

    Note: after some trial-and-error the checks boils down to nothing but
    non-empty values can be converted to non-negative floats... any field
    can be unpopulated, high/low may not hold, etc... for which the current
    code is overly complicated.
"""

import argparse
import datetime
import os

def getNonNegFloat(value):
  try: value = float(value)
  except ValueError: return None
  if value < 0: return None
  return value

def getOHLC(value):
  if value == '': return None, True
  value = getNonNegFloat(value)
  return value, value is not None

def checkOHLC(open_, high, low, close):
  open_, open_ok = getOHLC(open_)
  high, high_ok = getOHLC(high)
  low, low_ok = getOHLC(low)
  close, close_ok = getOHLC(close)
  if not open_ok or not high_ok or not low_ok or not close_ok: return False
  if high is None: high = float('Inf')
  if low is None: low = 0.0
  if open_ is None: open_ = low
  if close is None: close = high
  # Hack: in rare cases open/high/low/close are not populated, and high/low
  # may not really be high/low, so skip checking...
  #if open_ == 0.0 or high == 0.0 or low == 0.0 or close == 0.0: return True
  #if high < max(open_, low, close): return False
  #if low > min(open_, high, close): return False
  return True

def checkVolume(volume):
  # Volume can be unpopulated.
  if volume == '': return True
  volume = getNonNegFloat(volume)
  if volume is None: return False
  if int(volume) != volume: return False
  return True

def processLine(line):
  """ Processes one line from eod_file, sanity-checks data, and returns
      ticker and line of output.
  """
  assert line[-1] == '\n'
  line = line[:-1]
  (ticker, date, open_, high, low, close, volume, dividends, splits,
   adj_open, adj_high, adj_low, adj_close, adj_volume) = line.split(',')
  # Check date.
  try:
    tmp_date = datetime.datetime.strptime(date, '%Y-%m-%d')
  except ValueError:
    assert False, 'unsupported date format in line: %s' % line
  assert checkOHLC(open_, high, low, close), 'invalid OHLC in line: %s' % line
  assert checkOHLC(adj_open, adj_high, adj_low, adj_close), (
      'invalid adj OHLC in line: %s' % line)
  assert checkVolume(volume), 'invalid volume in line: %s' % line
  if adj_volume != '':
    adj_volume = getNonNegFloat(adj_volume)
    assert adj_volume is not None, 'invalid adj volume in line: %s' % line
  if dividends != '':
    dividends = getNonNegFloat(dividends)
    assert dividends is not None, 'invalid dividends in line: %s' % line
  if splits != '':
    splits = getNonNegFloat(splits)
    assert splits is not None, 'invalid splits in line: %s' % line

  return ticker, date, line

def convertEodRaw(eod_file, raw_dir, max_lines=0):
  # Since we always append to raw files (lines of a ticker may not be
  # adjacent in sf1_file) it's only sane to run this script with an
  # empty raw_dir.
  assert len(os.listdir(raw_dir)) == 0, (
      'nonempty raw dir: %s' % raw_dir)

  num_lines = 0
  output_ticker = None
  output_fp = None
  prev_date = None
  ticker_date = dict()

  with open(eod_file, 'r') as fp:
    while True:
      line = fp.readline()
      if line == '':
        break
      # Prepare output data.
      ticker, date, line = processLine(line)
      if ticker in ticker_date:
        assert date > ticker_date[ticker], 'non-increasing date in line: %s (prev: %s)' % (
            line, ticker_date[ticker])
      ticker_date[ticker] = date
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
  parser.add_argument('--eod_file', required=True,
                      help='unzipped file of entire EOD database from quandl')
  parser.add_argument('--raw_dir', required=True,
                      help='output dir of raw files')
  parser.add_argument('--max_lines', type=int, default=0,
                      help='max number of lines to process from eod_file; '
                           'only use this for debugging')
  args = parser.parse_args()
  convertEodRaw(args.eod_file, args.raw_dir, args.max_lines)

if __name__ == '__main__':
  main()

