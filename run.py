#!/usr/bin/python

""" Runs data collection, training, analysis and prediction.

    Steps:
    - make a new dir, eg, /Users/lnyang/lab/qd2/data/runs/20150530
    - make subdirs raw/sf1, raw/eod, raw/yahoo

    - download sf1 to raw/sf1:
      https://www.quandl.com/api/v3/databases/SF1/data?auth_token=KH43r2CQK7vmRodxQXX3
    - unzip and rename to sf1.csv
    - download indicators to raw/sf1/indicators.txt:
      http://www.sharadar.com/meta/indicators.txt

    - download eod to raw/eod:
      https://www.quandl.com/api/v3/databases/EOD/data?auth_token=KH43r2CQK7vmRodxQXX3
    - unzip and rename to eod.csv

    - download market data to raw/yahoo:
      http://real-chart.finance.yahoo.com/table.csv?s=%5ERUA (^RUA for russell 3000)
    - rename to market.csv

    - modify this script to update:
      - RUN_ID
"""

import logging
import os
import util

###############
## Constants ##
###############

RUN_ID = '20150530'
DRY_RUN = False

CODE_DIR = '/Users/lnyang/lab/qd2/qd2'
BASE_DIR = '/Users/lnyang/lab/qd2/data/runs'

RUN_DIR = '%s/%s' % (BASE_DIR, RUN_ID)

RAW_DIR = '%s/raw' % RUN_DIR
RAW_SF1_DIR = '%s/sf1' % RAW_DIR
RAW_EOD_DIR = '%s/eod' % RAW_DIR
RAW_YAHOO_DIR = '%s/yahoo' % RAW_DIR

RAW_SF1_FILE = '%s/sf1.csv' % RAW_SF1_DIR
SF1_INDICATOR_FILE = '%s/indicators.txt' % RAW_SF1_DIR
RAW_EOD_FILE = '%s/eod.csv' % RAW_EOD_DIR

TICKER_DIR = '%s/tickers' % RUN_DIR
SF1_TICKER_FILE = '%s/sf1_tickers' % TICKER_DIR
EOD_TICKER_FILE = '%s/eod_tickers' % TICKER_DIR
YAHOO_TICKER_FILE = '%s/yahoo_tickers' % TICKER_DIR

YAHOO_SF1_DIR = '%s/sf1' % RAW_YAHOO_DIR

SF1_DIR = '%s/sf1' % RUN_DIR
SF1_RAW_DIR = '%s/raw' % SF1_DIR
SF1_PROCESSED_DIR = '%s/processed' % SF1_DIR

PRICE_DATA = 'eod'  # 'eod' or 'yahoo'

LOG_LEVEL = logging.INFO

# Steps to execute, set to False to skip steps.
DO = {
    'get_sf1_tickers': False,
    'get_eod_tickers': False,
    'download_yahoo': False,
    'convert_sf1_raw': False,
    'process_sf1_raw': True,
}

####################
## Util functions ##
####################

# Checks and makes dir if not exist.
def maybeMakeDir(dir):
  if not os.path.isdir(dir):
    os.makedirs(dir)

# Checks to run or skip specified step, logs and returns decision.
def logDo(step):
  if DO[step]:
    logging.info('running step: %s' % step)
    return True
  logging.info('skipping step: %s' % step)
  return False

# Shortcut to util.run() with dry run option.
def run(cmd):
  util.run(cmd, dry_run=DRY_RUN)

############
## Script ##
############

util.configLogging(LOG_LEVEL)

# Make dirs.
maybeMakeDir(TICKER_DIR)
maybeMakeDir(YAHOO_SF1_DIR)
maybeMakeDir(SF1_RAW_DIR)
maybeMakeDir(SF1_PROCESSED_DIR)

if logDo('get_sf1_tickers'):
  cmd = '%s/get_sf1_tickers.py --sf1_file=%s --ticker_file=%s' % (
      CODE_DIR, RAW_SF1_FILE, SF1_TICKER_FILE)
  run(cmd)

if logDo('get_eod_tickers'):
  cmd = '%s/get_eod_tickers.py --eod_file=%s --ticker_file=%s' % (
      CODE_DIR, RAW_EOD_FILE, EOD_TICKER_FILE)
  run(cmd)

if logDo('download_yahoo'):
  cmd = '%s/download_yahoo.py --ticker_file=%s --download_dir=%s' % (
      CODE_DIR, SF1_TICKER_FILE, YAHOO_SF1_DIR)
  run(cmd)

if logDo('convert_sf1_raw'):
  cmd = ('%s/convert_sf1_raw.py --sf1_file=%s --indicator_file=%s '
         '--raw_dir=%s' % (
             CODE_DIR, RAW_SF1_FILE, SF1_INDICATOR_FILE, SF1_RAW_DIR))
  run(cmd)

if logDo('process_sf1_raw'):
  cmd = '%s/process_sf1_raw.py --raw_dir=%s --processed_dir=%s' % (
      CODE_DIR, SF1_RAW_DIR, SF1_PROCESSED_DIR)
  run(cmd)

