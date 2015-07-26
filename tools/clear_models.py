#!/usr/bin/python

import os

RUN_DIR = '/home/lnyang/lab/qd2/history/20150601/data/runs/20150601'

experiment_dir = '%s/experiments' % RUN_DIR
experiments = os.listdir(EXPERIMENT_DIR)

for experiment in experiments:
  model_dir = '%s/%s/models' % (experiment_dir, experiment)
  models = os.listdir(model_dir)
  max_date = '000000'
  max_model = None
  for model in models:
    p = model.find('-')
    assert p > 0
    q = model.find('-', p + 1)
    assert q > p
    date = model[p+1:q]
    assert len(date) == 6
    for c in date:
      assert c >= '0' and c <= '9'
    if date > max_date:
      max_date = date
      max_model = model
  assert max_model is not None
  print 'model_dir: %s, %d models, keeping %s' % (
      model_dir, len(models), max_model)
  for model in models:
    if model == max_model:
      continue
    os.remove('%s/%s/models/%s' % (experiment_dir, experiment, model))

