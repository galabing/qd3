#!/usr/bin/python2.7

# Adapted from qd (Q-results.py)
""" Simulates training/prediction over time.

    Stocks from each yyyymm will be grouped for prediction, and the model
    with right date (prediction date - prediction window - delay)
    will be used.  All stocks on that date will be scored and output will
    be written in the form of:
      date: yyyymm
      \tABC\tgain\tscore
      ...
      \tXYZ\tgain\tscore
    which can be used to simulate trading.

    See run_experiment for xample usage.
"""

import argparse
import logging
import numpy
import os
import pickle
import util

TMP_DATA_FILE = '/tmp/qd3_predict_all_tmp_data'

def getName(ym, prefix, suffix):
  y, m = ym.split('-')
  return '%s%s%s%s' % (prefix, y, m, suffix)

def prepareData(ym, data_file, label_file, meta_file, predict_meta_file,
                tmp_data_file):
  data_ifp = open(data_file, 'r')
  label_ifp = open(label_file, 'r')
  meta_ifp = open(meta_file, 'r')
  data_ofp = open(tmp_data_file, 'w')
  if predict_meta_file is None:
    predict_meta_ifp = None
    predict_meta = None
  else:
    predict_meta_ifp = open(predict_meta_file, 'r')
    predict_meta = predict_meta_ifp.readline()

  meta = []
  while True:
    line = meta_ifp.readline()
    if line == '':
      assert data_ifp.readline() == ''
      assert label_ifp.readline() == ''
      break
    assert line[-1] == '\n'
    data_line = data_ifp.readline()
    label_line = label_ifp.readline()
    assert data_line != ''
    assert label_line != ''

    if predict_meta is not None:
      if line != predict_meta:
        continue
      predict_meta = predict_meta_ifp.readline()

    ticker, date, tmp, gain = line[:-1].split('\t')
    if util.ymdToYm(date) != ym:
      continue
    assert data_line[-1] == '\n'
    assert label_line[-1] == '\n'
    label = float(label_line[:-1])
    gain = float(gain)
    # This is not true when labels are cut at other places than 0.
    # TODO: --label_file is not needed; remove.
    #if label > 0.5: assert gain >= 0
    #if label < 0.5: assert gain <= 0
    print >> data_ofp, data_line[:-1]
    meta.append([ticker, gain])

  data_ifp.close()
  label_ifp.close()
  meta_ifp.close()
  data_ofp.close()
  if predict_meta_ifp is not None:
    predict_meta_ifp.close()
  return meta

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_file', required=True)
  parser.add_argument('--label_file', required=True)
  parser.add_argument('--meta_file', required=True)
  # Similar to --train_meta_file in train_model.py
  parser.add_argument('--predict_meta_file')
  parser.add_argument('--model_dir', required=True)
  parser.add_argument('--model_prefix', required=True)
  parser.add_argument('--model_suffix', required=True)
  parser.add_argument('--imputer_dir', required=True)
  parser.add_argument('--imputer_prefix', required=True)
  parser.add_argument('--imputer_suffix', required=True)
  parser.add_argument('--prediction_window', type=int, required=True)
  parser.add_argument('--delay_window', type=int, required=True)
  parser.add_argument('--result_file', required=True)
  parser.add_argument('--allow_older_models', action='store_true')
  args = parser.parse_args()

  # get dates for prediction
  with open(args.meta_file, 'r') as fp:
    lines = fp.read().splitlines()
  dates = set()
  for line in lines:
    tmp1, date, tmp2, tmp3 = line.split('\t')
    dates.add(util.ymdToYm(date))
  dates = sorted(dates)

  ofp = open(args.result_file, 'w')

  started = False  # check no 'hole' in simulation period
  delta = args.prediction_window + args.delay_window
  previous_files = [None, None]  # model, imputer
  for date in dates:
    ym = util.getPreviousYm(date, delta)
    model_name = getName(ym, args.model_prefix, args.model_suffix)
    imputer_name = getName(ym, args.imputer_prefix, args.imputer_suffix)
    model_file = '%s/%s' % (args.model_dir, model_name)
    imputer_file = '%s/%s' % (args.imputer_dir, imputer_name)
    if not os.path.isfile(model_file):
      if args.allow_older_models and previous_files[0] is not None:
        model_file = previous_files[0]
        imputer_file = previous_files[1]
        logging.warn('using previous model %s for %s' % (model_file, date))
      else:
        assert not started
        continue

    assert os.path.isfile(imputer_file)
    started = True
    previous_files = [model_file, imputer_file]

    meta = prepareData(date, args.data_file, args.label_file, args.meta_file,
                       args.predict_meta_file, TMP_DATA_FILE)
    data = numpy.loadtxt(TMP_DATA_FILE)
    assert data.shape[0] == len(meta), 'inconsistent data size: %d vs %d' % (
        data.shape[0], len(meta))

    with open(imputer_file, 'rb') as fp:
      imputer = pickle.load(fp)
    data = imputer.transform(data)

    with open(model_file, 'rb') as fp:
      model = pickle.load(fp)

    if 'predict_proba' in dir(model):
      prob = model.predict_proba(data)
      prob = [item[1] for item in prob]
    else:
      prob = model.predict(data)

    assert len(prob) == len(meta)
    items = [[meta[i][0], meta[i][1], prob[i]]
             for i in range(len(prob))]
    items.sort(key=lambda item: item[2], reverse=True)
    print >> ofp, 'date: %s' % date
    for item in items:
      ticker, gain, score = item
      print >> ofp, '\t%s\t%f\t%f' % (ticker, gain, score)

  ofp.close()
  if os.path.isfile(TMP_DATA_FILE):
    os.remove(TMP_DATA_FILE)

if __name__ == '__main__':
  main()

