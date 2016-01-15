#!/usr/bin/python2.7

import argparse
import os
import util

ITEMS = [
#    ['close', [0, 1, 2, 3, 4], 1.0, True, True, 'window_week-'],
#    ['close', [0, 4, 8, 12, 16, 20], 1.0, True, True, 'window_month-'],
#    ['close', [0, 10, 20, 30, 40, 50, 60], 1.0, True, True, 'window_quarter-'],
#    ['close', [0, 40, 80, 120, 160, 200, 240], 1.0, True, True, 'window_year-'],
    ['close', range(66), 0.01, True, True, 'window_1x66-'],
    ['volume', range(66), 1.0, True, True, 'window_v_1x66-'],
]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--computer',
      default='/Users/lnyang/lab/qd2/qd2/compute_window_feature.py')
  parser.add_argument('--adjusted_dir', required=True,
                      help='dir of adusted yahoo data')
  parser.add_argument('--feature_base_dir', required=True)
  args = parser.parse_args()

  for label, windows, bonus, do_raw, do_fd, prefix in ITEMS:
    value_dir = '%s/%s' % (args.adjusted_dir, label)
    windows = ','.join(['%d' % window for window in windows])
    do_raw_arg = ''
    if do_raw:
      do_raw_arg = '--do_raw'
    do_fd_arg = ''
    if do_fd:
      do_fd_arg = '--do_fd'
    cmd = ('%s --value_dir=%s --windows=%s --bonus=%f'
           ' %s %s --feature_dir=%s --prefix=%s' % (
        args.computer, value_dir, windows, bonus, do_raw_arg, do_fd_arg,
        args.feature_base_dir, prefix))
    util.run(cmd)

if __name__ == '__main__':
  main()

