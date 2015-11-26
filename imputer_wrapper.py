#!/usr/bin/python2.6

from sklearn.preprocessing import Imputer
import numpy

class ImputerWrapper:
  """ A simple wrapper around Imputer and supports using zero to fill in missing values.
  """

  def __init__(self, missing_values='NaN', strategy='zero', axis=0, verbose=0, copy=False):
    self.strategy = strategy
    self.imputer = None
    if strategy != 'zero':
      self.imputer = Imputer(missing_values, strategy, axis, verbose, copy)

  def fit(self, X, y=None):
    if self.strategy == 'zero':
      return self
    self.imputer.fit(X, y)
    return self

  def fit_transform(self, X, y=None, **fit_params):
    if self.strategy == 'zero':
      for i in range(X.shape[0]):
        for j in range(X.shape[1]):
          if numpy.isnan(X[i][j]):
            X[i][j] = 0.0
      return X
    return self.imputer.fit_transform(X, y, **fit_params)

  def get_params(self, deep=True):
    if self.strategy == 'zero':
      return None
    return self.imputer.get_params(deep)

  def set_params(self, **params):
    if self.strategy == 'zero':
      return self
    self.imputer.set_params(**params)
    return self

  def transform(self, X):
    if self.strategy == 'zero':
      for i in range(X.shape[0]):
        for j in range(X.shape[1]):
          if numpy.isnan(X[i][j]):
            X[i][j] = 0.0
      return X
    return self.imputer.transform(X)

