#!/usr/bin/python2.7

import argparse
import pickle

def inspectModel(model_file, feature_file, topk, botk):
  with open(model_file, 'rb') as fp:
    model = pickle.load(fp)
  scores = model.feature_importances_

  with open(feature_file, 'r') as fp:
    features = [line for line in fp.read().splitlines()
                if not line.startswith('#')]
  assert len(features) == len(scores), (
      'inconsistent feature count: %d vs %d' % (len(features), len(scores)))

  topk = min(topk, len(scores))
  botk = min(botk, len(scores))
  items = sorted([[features[i], scores[i]] for i in range(len(scores))],
                 key=lambda item: item[1], reverse=True)

  print '%d features, showing top %d and bottom %d' % (
      len(items), topk, botk)
  for i in range(topk):
    print ' %d: %s = %f' % (i+1, items[i][0], items[i][1])
  print ' ...'
  for i in range(botk):
    j = len(items) - botk + i
    print ' %d: %s = %f' % (j+1, items[j][0], items[j][1])

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--model_file', required=True)
  parser.add_argument('--feature_file', required=True)
  parser.add_argument('--topk', type=int, default=20)
  parser.add_argument('--botk', type=int, default=20)
  args = parser.parse_args()
  inspectModel(args.model_file, args.feature_file, args.topk, args.botk)

if __name__ == '__main__':
  main()

