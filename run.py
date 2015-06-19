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

    - prepare feature lists under feature_lists dir
    - prepare experiment configs under configs dir

    - modify config.py to update:
      - RUN_ID
      - CONFIGS
      - etc

    TODOs:
    - add volume features -- need to modify eod/yahoo processing to collect avg volume
      of the month instead of that of the first day
"""

from config import *
import logging
import os
import util

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
    'get_eod_egain_label': False,
    'get_yahoo_egain_label': False,
    'compute_eod_logadjprice_feature': False,
    'compute_yahoo_logadjprice_feature': False,
    'compute_eod_gain_feature': False,
    'compute_yahoo_gain_feature': False,
    'compute_eod_egain_feature': False,
    'compute_yahoo_egain_feature': False,
    'run_experiments': True,
}

####################
## Util functions ##
####################

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
util.maybeMakeDirs([
    TICKER_DIR,
    YAHOO_SF1_DIR,
    SF1_RAW_DIR,
    SF1_PROCESSED_DIR,
    EOD_RAW_DIR,
    EOD_PROCESSED_DIR,
    YAHOO_PROCESSED_DIR,
    FEATURE_DIR,
    FEATURE_INFO_DIR,
    MISC_DIR,
    EOD_PRICE_DIR,
    EOD_ADJPRICE_DIR,
    EOD_LOGADJPRICE_DIR,
    YAHOO_PRICE_DIR,
    YAHOO_ADJPRICE_DIR,
    YAHOO_LOGADJPRICE_DIR,
    EOD_GAIN_DIR,
    YAHOO_GAIN_DIR,
    EOD_GAIN_LABEL_DIR,
    YAHOO_GAIN_LABEL_DIR,
    MARKET_PROCESSED_DIR,
    MARKET_ADJPRICE_DIR,
    MARKET_GAIN_DIR,
    EOD_EGAIN_DIR,
    YAHOO_EGAIN_DIR,
    EOD_EGAIN_LABEL_DIR,
    YAHOO_EGAIN_LABEL_DIR,
])

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
    util.maybeMakeDir(gain_dir)
    cmd = '%s/compute_gain.py --price_dir=%s --k=%d --gain_dir=%s' % (
        CODE_DIR, EOD_ADJPRICE_DIR, k, gain_dir)
    run(cmd)

if logDo('get_yahoo_gain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (YAHOO_GAIN_DIR, k)
    util.maybeMakeDir(gain_dir)
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
    util.maybeMakeDir(gain_dir)
    cmd = '%s/compute_gain.py --price_dir=%s --k=%d --gain_dir=%s' % (
        CODE_DIR, MARKET_ADJPRICE_DIR, k, gain_dir)
    run(cmd)

if logDo('get_eod_egain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (EOD_GAIN_DIR, k)
    for market in MARKETS:
      market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, k, market)
      egain_dir = '%s/%d/%s' % (EOD_EGAIN_DIR, k, market)
      util.maybeMakeDir(egain_dir)
      cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
             '--egain_dir=%s' % (CODE_DIR, gain_dir, market_file, egain_dir))
      run(cmd)

if logDo('get_yahoo_egain_feature'):
  for k in GAIN_K_LIST:
    gain_dir = '%s/%d' % (YAHOO_GAIN_DIR, k)
    for market in MARKETS:
      market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, k, market)
      egain_dir = '%s/%d/%s' % (YAHOO_EGAIN_DIR, k, market)
      util.maybeMakeDir(egain_dir)
      cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
             '--egain_dir=%s' % (CODE_DIR, gain_dir, market_file, egain_dir))
      run(cmd)

if logDo('get_eod_egain_label'):
  for market in MARKETS:
    market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, PREDICTION_WINDOW, market)
    egain_dir = '%s/%s' % (EOD_EGAIN_LABEL_DIR, market)
    util.maybeMakeDir(egain_dir)
    cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
           '--egain_dir=%s' % (
        CODE_DIR, EOD_GAIN_LABEL_DIR, market_file, egain_dir))
    run(cmd)

if logDo('get_yahoo_egain_label'):
  for market in MARKETS:
    market_file = '%s/%d/%s' % (MARKET_GAIN_DIR, PREDICTION_WINDOW, market)
    egain_dir = '%s/%s' % (YAHOO_EGAIN_LABEL_DIR, market)
    util.maybeMakeDir(egain_dir)
    cmd = ('%s/compute_egain.py --gain_dir=%s --market_file=%s '
           '--egain_dir=%s' % (
        CODE_DIR, YAHOO_GAIN_LABEL_DIR, market_file, egain_dir))
    run(cmd)

if logDo('compute_eod_logadjprice_feature'):
  for k in LOGADJPRICE_K_LIST:
    output_dir = '%s/eod-logadjprice-%d' % (FEATURE_DIR, k)
    util.maybeMakeDir(output_dir)
    cmd = ('%s/compute_previous_feature.py --feature_dir=%s --k=%d '
           '--pfeature_dir=%s' % (
        CODE_DIR, EOD_LOGADJPRICE_DIR, k, output_dir))
    run(cmd)

if logDo('compute_yahoo_logadjprice_feature'):
  for k in LOGADJPRICE_K_LIST:
    output_dir = '%s/yahoo-logadjprice-%d' % (FEATURE_DIR, k)
    util.maybeMakeDir(output_dir)
    cmd = ('%s/compute_previous_feature.py --feature_dir=%s --k=%d '
           '--pfeature_dir=%s' % (
        CODE_DIR, YAHOO_LOGADJPRICE_DIR, k, output_dir))
    run(cmd)

if logDo('compute_eod_gain_feature'):
  for k in GAIN_K_LIST:
    input_dir = '%s/%d' % (EOD_GAIN_DIR, k)
    output_dir = '%s/eod-gain-%d' % (FEATURE_DIR, k)
    util.maybeMakeDir(output_dir)
    cmd = ('%s/compute_previous_feature.py --feature_dir=%s --k=%d '
           '--pfeature_dir=%s' % (
        CODE_DIR, input_dir, k, output_dir))
    run(cmd)

if logDo('compute_yahoo_gain_feature'):
  for k in GAIN_K_LIST:
    input_dir = '%s/%d' % (YAHOO_GAIN_DIR, k)
    output_dir = '%s/yahoo-gain-%d' % (FEATURE_DIR, k)
    util.maybeMakeDir(output_dir)
    cmd = ('%s/compute_previous_feature.py --feature_dir=%s --k=%d '
           '--pfeature_dir=%s' % (
        CODE_DIR, input_dir, k, output_dir))
    run(cmd)

if logDo('compute_eod_egain_feature'):
  for k in GAIN_K_LIST:
    for market in MARKETS:
      input_dir = '%s/%d/%s' % (EOD_EGAIN_DIR, k, market)
      output_dir = '%s/eod-%s-egain-%d' % (FEATURE_DIR, market, k)
      util.maybeMakeDir(output_dir)
      cmd = ('%s/compute_previous_feature.py --feature_dir=%s --k=%d '
             '--pfeature_dir=%s' % (
          CODE_DIR, input_dir, k, output_dir))
      run(cmd)

if logDo('compute_yahoo_egain_feature'):
  for k in GAIN_K_LIST:
    for market in MARKETS:
      input_dir = '%s/%d/%s' % (YAHOO_EGAIN_DIR, k, market)
      output_dir = '%s/yahoo-%s-egain-%d' % (FEATURE_DIR, market, k)
      util.maybeMakeDir(output_dir)
      cmd = ('%s/compute_previous_feature.py --feature_dir=%s --k=%d '
             '--pfeature_dir=%s' % (
          CODE_DIR, input_dir, k, output_dir))
      run(cmd)

if logDo('run_experiments'):
  for experiment in EXPERIMENTS:
    config_file = '%s/%s.json' % (CONFIG_DIR, experiment)
    cmd = '%s/run_experiment.py --config=%s' % (CODE_DIR, config_file)
    run(cmd)

