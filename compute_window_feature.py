#!/usr/bin/python2.7

""" Computes window features.

    Example usage:
      ./compute_window_feature.py --value_dir=./adjusted/close
                                  --windows=0,4,8,12,16,20
                                  --bonus=1
                                  --do_raw
                                  --do_fd
                                  --feature_dir=./features
                                  --prefix=window_month-

    --windows: comma-separated sample steps, going back in time
               (0 is current date, 4 is 4 trading days before, etc)
    --do_raw: output raw sampled values
    --do_fd: output first derivatives of sampled values
    --prefix: output prefix (window_month-0, window_month-4, etc)
"""

import argparse
import os
import util

def computeWindowFeature(args):
  assert args.do_raw or args.do_fd
  tickers = sorted(os.listdir(args.value_dir))
  windows = [int(window) for window in args.windows.split(',')]
  assert min(windows) >= 0, 'cannot look at future values'
  assert len(windows) > 0
  assert len(windows) > 1 or not args.do_fd
  max_window = max(windows)

  for ticker in tickers:
    raw_fps = None
    fd_fps = None
    if args.do_raw:
      raw_fps = []
      for window in windows:
        raw_dir = '%s/%s%d' % (args.feature_dir, args.prefix, window)
        if not os.path.isdir(raw_dir):
          os.mkdir(raw_dir)
        raw_fps.append(open('%s/%s' % (raw_dir, ticker), 'w'))
    if args.do_fd:
      fd_fps = []
      for i in range(len(windows)-1):
        fd_dir = '%s/%sfd-%d' % (args.feature_dir, args.prefix, windows[i])
        if not os.path.isdir(fd_dir):
          os.mkdir(fd_dir)
        fd_fps.append(open('%s/%s' % (fd_dir, ticker), 'w'))
        
    dvalues = util.readKeyValueList('%s/%s' % (args.value_dir, ticker))
    for i in range(max_window, len(dvalues)):
      values = [dvalues[i-window][1] for window in windows]
      if raw_fps:
        raws = util.normalize(values)
        assert len(raws) == len(raw_fps)
        for j in range(len(raws)):
          print >> raw_fps[j], '%s\t%f' % (dvalues[i][0], raws[j])
      if fd_fps:
        derivatives = [(values[j] - values[j+1]) / (values[j+1] + args.bonus) for j in range(len(windows)-1)]
        derivatives = util.normalize(derivatives)
        assert len(derivatives) == len(fd_fps)
        for j in range(len(derivatives)):
          print >> fd_fps[j], '%s\t%f' % (dvalues[i][0], derivatives[j])
    if raw_fps:
      for fp in raw_fps:
        fp.close()
    if fd_fps:
      for fp in fd_fps:
        fp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--value_dir', required=True)
  parser.add_argument('--windows', required=True)
  parser.add_argument('--bonus', type=float, required=True)
  parser.add_argument('--do_raw', action='store_true')
  parser.add_argument('--do_fd', action='store_true')
  parser.add_argument('--feature_dir', required=True)
  parser.add_argument('--prefix', required=True)
  computeWindowFeature(parser.parse_args())

if __name__ == '__main__':
  main()

