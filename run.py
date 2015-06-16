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
    - download ticker info to raw/sf1/tickers.txt:
      http://www.sharadar.com/meta/tickers.txt

    - download eod to raw/eod:
      https://www.quandl.com/api/v3/databases/EOD/data?auth_token=KH43r2CQK7vmRodxQXX3
    - unzip and rename to eod.csv

    - download market data to raw/yahoo/market:
      http://real-chart.finance.yahoo.com/table.csv?s=%5ERUA (^RUA for russell 3000)
      http://real-chart.finance.yahoo.com/table.csv?s=%5EGSPC (^GSPC for sp 500)
    - rename to R3000.csv, SP500.csv etc

    - modify this script to update:
      - RUN_ID
      - MARKETS

    TODOs:
    - add volume features -- need to modify eod/yahoo processing to collect avg volume
      of the month instead of that of the first day
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
SF1_SECIND_FILE = '%s/tickers.txt' % RAW_SF1_DIR
RAW_EOD_FILE = '%s/eod.csv' % RAW_EOD_DIR

TICKER_DIR = '%s/tickers' % RUN_DIR
SF1_TICKER_FILE = '%s/sf1_tickers' % TICKER_DIR
EOD_TICKER_FILE = '%s/eod_tickers' % TICKER_DIR
YAHOO_TICKER_FILE = '%s/yahoo_tickers' % TICKER_DIR

YAHOO_SF1_DIR = '%s/sf1' % RAW_YAHOO_DIR
YAHOO_MARKET_DIR = '%s/market' % RAW_YAHOO_DIR
MARKETS = ['R3000', 'SP500']

SF1_DIR = '%s/sf1' % RUN_DIR
SF1_RAW_DIR = '%s/raw' % SF1_DIR
SF1_PROCESSED_DIR = '%s/processed' % SF1_DIR

EOD_DIR = '%s/eod' % RUN_DIR
EOD_RAW_DIR = '%s/raw' % EOD_DIR
EOD_PROCESSED_DIR = '%s/processed' % EOD_DIR
EOD_PRICE_DIR = '%s/price' % EOD_DIR
EOD_ADJPRICE_DIR = '%s/adjprice' % EOD_DIR
EOD_LOGADJPRICE_DIR = '%s/logadjprice' % EOD_DIR
EOD_GAIN_DIR = '%s/gain' % EOD_DIR
EOD_EGAIN_DIR = '%s/egain' % EOD_DIR

YAHOO_DIR = '%s/yahoo' % RUN_DIR
YAHOO_PROCESSED_DIR = '%s/processed' % YAHOO_DIR
YAHOO_PRICE_DIR = '%s/price' % YAHOO_DIR
YAHOO_ADJPRICE_DIR = '%s/adjprice' % YAHOO_DIR
YAHOO_LOGADJPRICE_DIR = '%s/logadjprice' % YAHOO_DIR
YAHOO_GAIN_DIR = '%s/gain' % YAHOO_DIR
YAHOO_EGAIN_DIR = '%s/egain' % YAHOO_DIR

MARKET_DIR = '%s/market' % RUN_DIR
MARKET_PROCESSED_DIR = '%s/processed' % MARKET_DIR
MARKET_ADJPRICE_DIR = '%s/adjprice' % MARKET_DIR
MARKET_GAIN_DIR = '%s/gain' % MARKET_DIR

FEATURE_DIR = '%s/features' % RUN_DIR
FEATURE_INFO_DIR = '%s/feature_info' % RUN_DIR

MISC_DIR = '%s/misc' % RUN_DIR
FEATURE_STATS_FILE = '%s/feature_stats.tsv' % MISC_DIR
SECTOR_STATS_FILE = '%s/sector_stats' % MISC_DIR
INDUSTRY_STATS_FILE = '%s/industry_stats' % MISC_DIR

# For features, we look at many time windows, and we do not
# enforce any minimum raw price.
GAIN_K_LIST = [1, 2, 3, 6, 9, 12, 15, 18, 21, 24,
               27, 30, 33, 36, 39, 42, 45, 48]
# For labels, we only predict a 12-month window, and we enforce
# a minimum raw price for all transactions.
PREDICTION_WINDOW = 12
MIN_RAW_PRICE = 10
EOD_GAIN_LABEL_DIR = '%s/gain%d/%d' % (
    EOD_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)
YAHOO_GAIN_LABEL_DIR = '%s/gain%d/%d' % (
    YAHOO_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)
EOD_EGAIN_LABEL_DIR = '%s/egain%d/%d' % (
    EOD_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)
YAHOO_EGAIN_LABEL_DIR = '%s/egain%d/%d' % (
    YAHOO_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)

LOG_LEVEL = logging.INFO

# Steps to execute, set to False to skip steps.
DO_EVERYTHING = False  # if True, overwrites DO map
DO = {
    'get_sf1_tickers': False,
    'get_eod_tickers': False,
    'download_yahoo': False,
    'convert_sf1_raw': False,
    'process_sf1_raw': False,
    'convert_eod_raw': False,
    'process_eod_raw': False,
    'process_yahoo': False,
    'compute_basic_features': False,
    'compute_log_features': False,
    'get_feature_stats': False,
    'get_sector': False,
    'get_industry': False,
    'get_eod_price': False,
    'get_eod_adjprice': False,
    'get_eod_logadjprice': False,
    'get_yahoo_price': False,
    'get_yahoo_adjprice': False,
    'get_yahoo_logadjprice': False,
    'get_eod_gain_feature': False,
    'get_yahoo_gain_feature': False,
    'get_eod_gain_label': False,
    'get_yahoo_gain_label': False,
    'process_market': False,
    'get_market_adjprice': False,
    'get_market_gain': False,
    'get_eod_egain_feature': False,
    'get_yahoo_egain_feature': False,
    'get_eod_egain_label': True,
    'get_yahoo_egain_label': True,
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
  if DO_EVERYTHING:
    return True
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

# Prepare dirs.
maybeMakeDir(TICKER_DIR)
maybeMakeDir(YAHOO_SF1_DIR)
maybeMakeDir(SF1_RAW_DIR)
maybeMakeDir(SF1_PROCESSED_DIR)
maybeMakeDir(EOD_RAW_DIR)
maybeMakeDir(EOD_PROCESSED_DIR)
maybeMakeDir(YAHOO_PROCESSED_DIR)
maybeMakeDir(FEATURE_DIR)
maybeMakeDir(FEATURE_INFO_DIR)
maybeMakeDir(MISC_DIR)
maybeMakeDir(EOD_PRICE_DIR)
maybeMakeDir(EOD_ADJPRICE_DIR)
maybeMakeDir(EOD_LOGADJPRICE_DIR)
maybeMakeDir(YAHOO_PRICE_DIR)
maybeMakeDir(YAHOO_ADJPRICE_DIR)
maybeMakeDir(YAHOO_LOGADJPRICE_DIR)
maybeMakeDir(EOD_GAIN_DIR)
maybeMakeDir(YAHOO_GAIN_DIR)
maybeMakeDir(EOD_GAIN_LABEL_DIR)
maybeMakeDir(YAHOO_GAIN_LABEL_DIR)
maybeMakeDir(MARKET_PROCESSED_DIR)
maybeMakeDir(MARKET_ADJPRICE_DIR)
maybeMakeDir(MARKET_GAIN_DIR)
maybeMakeDir(EOD_EGAIN_DIR)
maybeMakeDir(YAHOO_EGAIN_DIR)
maybeMakeDir(EOD_EGAIN_LABEL_DIR)
maybeMakeDir(YAHOO_EGAIN_LABEL_DIR)

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

if logDo('convert_eod_raw'):
  cmd = '%s/convert_eod_raw.py --eod_file=%s --raw_dir=%s' % (
      CODE_DIR, RAW_EOD_FILE, EOD_RAW_DIR)
  run(cmd)

if logDo('process_eod_raw'):
  cmd = ('%s/process_eod_raw.py --raw_dir=%s --ticker_file=%s '
         '--processed_dir=%s' % (
             CODE_DIR, EOD_RAW_DIR, SF1_TICKER_FILE, EOD_PROCESSED_DIR))
  run(cmd)

if logDo('process_yahoo'):
  cmd = '%s/process_yahoo.py --raw_dir=%s --processed_dir=%s' % (
      CODE_DIR, YAHOO_SF1_DIR, YAHOO_PROCESSED_DIR)
  run(cmd)

if logDo('compute_basic_features'):
  cmd = ('%s/compute_basic_features.py --processed_dir=%s --ticker_file=%s '
         '--feature_base_dir=%s --info_dir=%s') % (
      CODE_DIR, SF1_PROCESSED_DIR, SF1_TICKER_FILE,
      FEATURE_DIR, FEATURE_INFO_DIR)
  run(cmd)

if logDo('compute_log_features'):
  cmd = ('%s/compute_log_features.py --processed_dir=%s --ticker_file=%s '
         '--feature_base_dir=%s --info_dir=%s') % (
      CODE_DIR, SF1_PROCESSED_DIR, SF1_TICKER_FILE,
      FEATURE_DIR, FEATURE_INFO_DIR)
  run(cmd)

if logDo('get_feature_stats'):
  cmd = '%s/get_feature_stats.py --info_dir=%s --stats_file=%s' % (
      CODE_DIR, FEATURE_INFO_DIR, FEATURE_STATS_FILE)
  run(cmd)

if logDo('get_sector'):
  cmd = ('%s/get_sector_industry.py --ticker_file=%s --info_file=%s '
         '--sector --output_base_dir=%s --stats_file=%s' % (
      CODE_DIR, SF1_TICKER_FILE, SF1_SECIND_FILE, FEATURE_DIR,
      SECTOR_STATS_FILE))
  run(cmd)

if logDo('get_industry'):
  cmd = ('%s/get_sector_industry.py --ticker_file=%s --info_file=%s '
         '--industry --output_base_dir=%s --stats_file=%s' % (
      CODE_DIR, SF1_TICKER_FILE, SF1_SECIND_FILE, FEATURE_DIR,
      INDUSTRY_STATS_FILE))
  run(cmd)

if logDo('get_eod_price'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=price '
         '--output_dir=%s' % (
      CODE_DIR, EOD_PROCESSED_DIR, EOD_PRICE_DIR))
  run(cmd)

if logDo('get_eod_adjprice'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=adjprice '
         '--output_dir=%s' % (
      CODE_DIR, EOD_PROCESSED_DIR, EOD_ADJPRICE_DIR))
  run(cmd)

if logDo('get_eod_logadjprice'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=adjprice '
         '--take_log --output_dir=%s' % (
      CODE_DIR, EOD_PROCESSED_DIR, EOD_LOGADJPRICE_DIR))
  run(cmd)

if logDo('get_yahoo_price'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=price '
         '--output_dir=%s' % (
      CODE_DIR, YAHOO_PROCESSED_DIR, YAHOO_PRICE_DIR))
  run(cmd)

if logDo('get_yahoo_adjprice'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=adjprice '
         '--output_dir=%s' % (
      CODE_DIR, YAHOO_PROCESSED_DIR, YAHOO_ADJPRICE_DIR))
  run(cmd)

if logDo('get_yahoo_logadjprice'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=adjprice '
         '--take_log --output_dir=%s' % (
      CODE_DIR, YAHOO_PROCESSED_DIR, YAHOO_LOGADJPRICE_DIR))
  run(cmd)

if logDo('get_eod_gain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (EOD_GAIN_DIR, k)
    maybeMakeDir(gain_dir)
    cmd = '%s/compute_gain.py --price_dir=%s --k=%d --gain_dir=%s' % (
        CODE_DIR, EOD_ADJPRICE_DIR, k, gain_dir)
    run(cmd)

if logDo('get_yahoo_gain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (YAHOO_GAIN_DIR, k)
    maybeMakeDir(gain_dir)
    cmd = '%s/compute_gain.py --price_dir=%s --k=%d --gain_dir=%s' % (
        CODE_DIR, YAHOO_ADJPRICE_DIR, k, gain_dir) 
    run(cmd)

if logDo('get_eod_gain_label'):
  cmd = ('%s/compute_gain.py --price_dir=%s --k=%d --min_raw_price=%f '
         '--raw_price_dir=%s --gain_dir=%s' % (
      CODE_DIR, EOD_ADJPRICE_DIR, PREDICTION_WINDOW, MIN_RAW_PRICE,
      EOD_PRICE_DIR, EOD_GAIN_LABEL_DIR))
  run(cmd)

if logDo('get_yahoo_gain_label'):
  cmd = ('%s/compute_gain.py --price_dir=%s --k=%d --min_raw_price=%f '
         '--raw_price_dir=%s --gain_dir=%s' % (
      CODE_DIR, YAHOO_ADJPRICE_DIR, PREDICTION_WINDOW, MIN_RAW_PRICE,
      YAHOO_PRICE_DIR, YAHOO_GAIN_LABEL_DIR))
  run(cmd)

if logDo('process_market'):
  cmd = '%s/process_yahoo.py --raw_dir=%s --processed_dir=%s' % (
      CODE_DIR, YAHOO_MARKET_DIR, MARKET_PROCESSED_DIR)
  run(cmd)

if logDo('get_market_adjprice'):
  cmd = ('%s/get_price_volume.py --processed_dir=%s --column=adjprice '
         '--output_dir=%s' % (
      CODE_DIR, MARKET_PROCESSED_DIR, MARKET_ADJPRICE_DIR))
  run(cmd)

if logDo('get_market_gain'):
  # For market we only do one version of gain (without mininum raw price)
  # and it will be used for both features and labels.  GAIN_K_LIST specify
  # all the windows for features, and [PREDICTION_WINDOW] specify those
  # for labels.  (Since PREDICTION_WINDOW = 12 which is in GAIN_K_LIST
  # this is no-op for now.)
  k_list = set(GAIN_K_LIST + [PREDICTION_WINDOW])
  for k in sorted(k_list):
    gain_dir = '%s/%d' % (MARKET_GAIN_DIR, k)
    maybeMakeDir(gain_dir)
    cmd = '%s/compute_gain.py --price_dir=%s --k=%d --gain_dir=%s' % (
        CODE_DIR, MARKET_ADJPRICE_DIR, k, gain_dir)
    run(cmd)

if logDo('get_eod_egain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (EOD_GAIN_DIR, k)
    for market in MARKETS:
      market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, k, market)
      egain_dir = '%s/%d/%s' % (EOD_EGAIN_DIR, k, market)
      maybeMakeDir(egain_dir)
      cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
             '--egain_dir=%s' % (CODE_DIR, gain_dir, market_file, egain_dir))
      run(cmd)

if logDo('get_yahoo_egain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (YAHOO_GAIN_DIR, k)
    for market in MARKETS:
      market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, k, market)
      egain_dir = '%s/%d/%s' % (YAHOO_EGAIN_DIR, k, market)
      maybeMakeDir(egain_dir)
      cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
             '--egain_dir=%s' % (CODE_DIR, gain_dir, market_file, egain_dir))
      run(cmd)

if logDo('get_eod_egain_label'):
  for market in MARKETS:
    market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, PREDICTION_WINDOW, market)
    egain_dir = '%s/%s' % (EOD_EGAIN_LABEL_DIR, market)
    maybeMakeDir(egain_dir)
    cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
           '--egain_dir=%s' % (
        CODE_DIR, EOD_GAIN_LABEL_DIR, market_file, egain_dir))
    run(cmd)

if logDo('get_yahoo_egain_label'):
  for market in MARKETS:
    market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, PREDICTION_WINDOW, market)
    egain_dir = '%s/%s' % (YAHOO_EGAIN_LABEL_DIR, market)
    maybeMakeDir(egain_dir)
    cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
           '--egain_dir=%s' % (
        CODE_DIR, YAHOO_GAIN_LABEL_DIR, market_file, egain_dir))
    run(cmd)

