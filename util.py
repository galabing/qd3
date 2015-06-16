import logging
import os

# Configures logging format.
def configLogging(level=logging.INFO):
  logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                      level=level)

# Runs command and maybe checks success.
def run(cmd, check=True, dry_run=False):
  logging.info('running command: %s' % cmd)
  if dry_run:
    return 0
  result = os.system(cmd)
  if check:
    assert result == 0
  return result

################
## Date utils ##
################

def ymdToY(ymd):
  y, m, d = ymd.split('-')
  return y

def ymdToYm(ymd):
  y, m, d = ymd.split('-')
  return '%s-%s' % (y, m)

def getNextYm(ym, k=1):
  assert k >= 0
  y, m = ym.split('-')
  y = int(y)
  m = int(m)
  y += int(k/12)
  m += k % 12
  if m > 12:
    m -= 12
    y += 1
  return '%02d-%02d' % (y, m)

##############
## IO utils ##
##############

def readTickers(ticker_file):
  with open(ticker_file, 'r') as fp:
    return sorted(fp.read().splitlines())

## Sf1

def parseSf1(lines):
  """ Parses processed sf1 lines into a dict: date => {indicator: value}.
  """
  assert len(lines) > 0
  headers = lines[0].split('\t')
  assert len(headers) > 0
  assert all([header != '' for header in headers])
  assert headers[0] == 'date', 'unknown key column: %s' % headers[0]
  data = dict()
  for i in range(1, len(lines)):
    items = lines[i].split('\t')
    assert len(items) == len(headers)
    row = dict()
    for j in range(1, len(headers)):
      if items[j] != '':
        row[headers[j]] = float(items[j])
    data[items[0]] = row
  return data

def readSf1(sf1_file):
  with open(sf1_file, 'r') as fp:
    lines = fp.read().splitlines()
  return parseSf1(lines)

def readSf1Column(sf1_file, header):
  if not os.path.isfile(sf1_file):
    return None
  data = readSf1(sf1_file)
  dcolumn = []
  for date in sorted(data.keys()):
    feature = data[date].get(header)
    dcolumn.append([date, feature])
  return dcolumn

## Feature stats (TODO: clean up code)

def updateCountDict(count_dict, key):
  if key not in count_dict: count_dict[key] = 1
  else: count_dict[key] += 1

def updateListDict(list_dict, key, value):
  if key not in list_dict: list_dict[key] = [value]
  else: list_dict[key].append(value)

def computeFeatureStats(feature_info):
  """ Computes feature stats.
      features: [(y, f), (y, f), ...] where f is either float or None
                indicating nonexistent feature value.
      returns: dict of y => [count, total, avg, min, 1p, 10p, 25p, 50p,
                             75p, 90p, 99p, max]
      Feature coverage = count / total, eg.
  """
  ncounts = dict()  # y => #None
  values = dict()  # y => [non-None values]
  for y, f in feature_info:
    if f is None:
      updateCountDict(ncounts, y)
    else:
      updateListDict(values, y, f)
  stats = dict()
  for y, v in values.iteritems():
    v.sort()
    lenv = len(v)
    stats[y] = [lenv, lenv + ncounts.get(y, 0), sum(v)/lenv, v[0],
                v[int(lenv*0.01)], v[int(lenv*0.1)],
                v[int(lenv*0.25)], v[int(lenv*0.5)],
                v[int(lenv*0.75)], v[int(lenv*0.9)],
                v[int(lenv*0.99)], v[-1]]
  for y, n in ncounts.iteritems():
    if y not in stats:
      stats[y] = [0, n, None, None, None, None, None, None, None,
                  None, None, None]
  return stats

def i2s(i):
  if i is None: return '-'
  return '%d' % i

def f2s(f):
  if f is None: return '-'
  return '%.6f' % f

def p2s(p):
  if p is None: return '-'
  return '%.2f%%' % (p*100)

def writeFeatureInfo(args, feature_info, info_file):
  stats = computeFeatureStats(feature_info)
  with open(info_file, 'w') as fp:
    print >> fp, 'args: %s' % args
    print >> fp, '\t'.join(['year', 'count', 'total', 'coverage',
                            'avg', 'min', '1perc', '10perc', '25perc',
                            '50perc', '75perc', '90perc', '99perc', 'max'])
    for year in sorted(stats.keys()):
      count, total, avg, min_, p1, p10, p25, p50, p75, p90, p99, max_ = (
          stats[year])
      coverage = float(count)/total
      print >> fp, '\t'.join([year, i2s(count), i2s(total), p2s(coverage),
                              f2s(avg), f2s(min_), f2s(p1), f2s(p10),
                              f2s(p25), f2s(p50), f2s(p75), f2s(p90),
                              f2s(p99), f2s(max_)])

def readKeyValueList(kv_file):
  """ Reads features or gains file with each line being <key>\t<value>,
      into a list of [[key, value], ...]
  """
  with open(kv_file, 'r') as fp:
    lines = fp.read().splitlines()
  kv = []
  for line in lines:
    k, v = line.split('\t')
    kv.append([k, float(v)])
  return kv

