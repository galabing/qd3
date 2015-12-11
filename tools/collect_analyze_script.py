#!/usr/bin/python2.7

import os
import shutil

EXPERIMENT_DIR = '/home/lnyang/lab/qd2/data/runs/20151101/experiments'
EXPERIMENTS = [
    'J',
    'J2',
    'J3',
    'J3MinPrice5',
    'J4',
    'J5',
    'J6',
    'J7A',
    'J7B',
    'J7C',
    'J7D',
    'J7E',
    'J7E200',
    'J7N10P10',
    'J7N5P5',
    'J7P10',
    'J7V25',
    'J7V50',
    'J7V75',
]
MODEL = None  #'RandomForestClassifier-201411--1'

OUTPUT_DIR = '/home/lnyang/tmp/qd2_experiments'

if os.path.isdir(OUTPUT_DIR):
  shutil.rmtree(OUTPUT_DIR)
os.mkdir(OUTPUT_DIR)

for exp in EXPERIMENTS:
  src = '%s/%s/analyze' % (EXPERIMENT_DIR, exp)
  dst = '%s/%s/analyze' % (OUTPUT_DIR, exp)
  shutil.copytree(src, dst)

  if MODEL is not None:
    src = '%s/%s/models/%s' % (EXPERIMENT_DIR, exp, MODEL)
    dst = '%s/%s/models' % (OUTPUT_DIR, exp)
    os.mkdir(dst)
    shutil.copy(src, dst)

