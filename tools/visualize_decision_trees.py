#!/Users/lnyang/miniconda2/bin/python2.7

from sklearn import tree
from sklearn.externals.six import StringIO
import argparse
import os
import pickle
import pydot

def visualize(model_file, feature_file, output_dir):
  with open(model_file, 'rb') as fp:
    model = pickle.load(fp)
  with open(feature_file, 'r') as fp:
    features = [line for line in fp.read().splitlines()
                if not line.startswith('#')]
  print '%d features' % len(features)
  if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
  for i in range(len(model.estimators_)):
    print 'visualizing tree %d/%d' % (i+1, len(model.estimators_))
    dot_data = StringIO()
    tree.export_graphviz(model.estimators_[i], feature_names=features,
                         class_names=['neg', 'pos'], filled=True,
                         out_file=dot_data)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_png('%s/tree-%d.png' % (output_dir, i))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--model_file', required=True)
  parser.add_argument('--feature_file', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()
  visualize(args.model_file, args.feature_file, args.output_dir)

if __name__ == '__main__':
  main()

