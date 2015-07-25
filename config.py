import socket

# Local or remote.
HOST = socket.gethostname()
assert HOST == 'lnyang-mn1' or HOST == 'lnyang-ld1'
if HOST == 'lnyang-mn1':
  HOST_DIR = '/Users/lnyang/lab/qd2'
else:
  assert HOST == 'lnyang-ld1'
  HOST_DIR = '/home/lnyang/lab/qd2'

###############
## Constants ##
###############

RUN_ID = '20150701'
EXPERIMENTS = [
]

MARKETS = ['R3000', 'SP500']
DRY_RUN = False

# For features, we look at many time windows, and we do not
# enforce any minimum raw price.
GAIN_K_LIST = [1, 2, 3, 6, 9, 12, 15, 18, 21, 24,
               27, 30, 33, 36, 39, 42, 45, 48]
LOGADJPRICE_K_LIST = [1, 2, 3, 6, 9, 12, 15, 18, 21, 24,
                      27, 30, 33, 36, 39, 42, 45, 48]
LOGADJVOLUME_K_LIST = [1, 2, 3, 6, 9, 12, 15, 18, 21, 24,
                       27, 30, 33, 36, 39, 42, 45, 48]
# For labels, we only predict a 12-month window, and we enforce
# a minimum raw price and/or membership for all transactions.
PREDICTION_WINDOW = 12
#MIN_RAW_PRICE = 0
MEMBERSHIP = 'SP500'

CODE_DIR = '%s/qd2' % HOST_DIR

BASE_DIR = '%s/data/runs' % HOST_DIR
RUN_DIR = '%s/%s' % (BASE_DIR, RUN_ID)

# This dir is for convenience purpose only (eg, MEMBERSHIP_DIR
# is assigned to it if MEMBERSHIP is None).  No input/output files
# should exist there.
#NOT_USED_DIR = '%s/not_used' % RUN_DIR

SYMBOL_DIR = '%s/symbols' % RUN_DIR

RAW_DIR = '%s/raw' % RUN_DIR
RAW_SF1_DIR = '%s/sf1' % RAW_DIR
RAW_EOD_DIR = '%s/eod' % RAW_DIR
RAW_YAHOO_DIR = '%s/yahoo' % RAW_DIR
RAW_MISC_DIR = '%s/misc' % RAW_DIR

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

SF1_DIR = '%s/sf1' % RUN_DIR
SF1_RAW_DIR = '%s/raw' % SF1_DIR
SF1_PROCESSED_DIR = '%s/processed' % SF1_DIR

EOD_DIR = '%s/eod' % RUN_DIR
EOD_RAW_DIR = '%s/raw' % EOD_DIR
EOD_PROCESSED_DIR = '%s/processed' % EOD_DIR
EOD_PRICE_DIR = '%s/price' % EOD_DIR
EOD_ADJPRICE_DIR = '%s/adjprice' % EOD_DIR
EOD_LOGADJPRICE_DIR = '%s/logadjprice' % EOD_DIR
EOD_LOGADJVOLUME_DIR = '%s/logadjvolume' % EOD_DIR
EOD_GAIN_DIR = '%s/gain' % EOD_DIR
EOD_EGAIN_DIR = '%s/egain' % EOD_DIR

YAHOO_DIR = '%s/yahoo' % RUN_DIR
YAHOO_PROCESSED_DIR = '%s/processed' % YAHOO_DIR
YAHOO_PRICE_DIR = '%s/price' % YAHOO_DIR
YAHOO_ADJPRICE_DIR = '%s/adjprice' % YAHOO_DIR
YAHOO_LOGADJPRICE_DIR = '%s/logadjprice' % YAHOO_DIR
YAHOO_LOGADJVOLUME_DIR = '%s/logadjvolume' % YAHOO_DIR
YAHOO_GAIN_DIR = '%s/gain' % YAHOO_DIR
YAHOO_EGAIN_DIR = '%s/egain' % YAHOO_DIR

MARKET_DIR = '%s/market' % RUN_DIR
MARKET_PROCESSED_DIR = '%s/processed' % MARKET_DIR
MARKET_ADJPRICE_DIR = '%s/adjprice' % MARKET_DIR
MARKET_GAIN_DIR = '%s/gain' % MARKET_DIR

FEATURE_DIR = '%s/features' % RUN_DIR
FEATURE_INFO_DIR = '%s/feature_info' % RUN_DIR
FEATURE_LIST_DIR = '%s/feature_lists' % RUN_DIR

MISC_DIR = '%s/misc' % RUN_DIR
FEATURE_STATS_FILE = '%s/feature_stats.tsv' % MISC_DIR
SECTOR_STATS_FILE = '%s/sector_stats' % MISC_DIR
INDUSTRY_STATS_FILE = '%s/industry_stats' % MISC_DIR
MEMBERSHIP_FILE = '%s/%s-membership' % (MISC_DIR, MEMBERSHIP)
#if MEMBERSHIP is not None:
#  MEMBERSHIP_DIR = '%s/%s-membership' % (MISC_DIR, MEMBERSHIP)
#else:
#  MEMBERSHIP_DIR = NOT_USED_DIR

#EOD_GAIN_LABEL_DIR = '%s/gain%d/%d' % (
#    EOD_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)
#YAHOO_GAIN_LABEL_DIR = '%s/gain%d/%d' % (
#    YAHOO_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)
#EOD_EGAIN_LABEL_DIR = '%s/egain%d/%d' % (
#    EOD_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)
#YAHOO_EGAIN_LABEL_DIR = '%s/egain%d/%d' % (
#    YAHOO_DIR, MIN_RAW_PRICE, PREDICTION_WINDOW)

CONFIG_DIR = '%s/configs' % RUN_DIR
EXPERIMENT_BASE_DIR = '%s/experiments' % RUN_DIR

