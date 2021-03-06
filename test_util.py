#!/usr/bin/python2.7

import math
import util

def checkFloatLists(expected, actual):
  assert len(actual) == len(expected), '%d vs %d' % (len(actual), len(expected))
  for i in range(len(expected)):
    assert abs(actual[i] - expected[i]) < 1e-9

def test_normalize():
  assert util.normalize([1.0]) == [0.0]
  assert util.normalize([1.0, 1.0]) == [0.0, 0.0]
  checkFloatLists([-math.sqrt(2.0)/2, math.sqrt(2.0)/2], util.normalize([1.0, 2.0]))
  checkFloatLists([-math.sqrt(2.0)/2, 0.0, math.sqrt(2.0)/2], util.normalize([1.0, 2.0, 3.0]))
  checkFloatLists([0.5, -0.5, 0.5, -0.5], util.normalize([10.0, -10.0, 10.0, -10.0]))

def test_getPreviousYmd():
  assert util.getPreviousYmd('2000-01-01', 0) == '2000-01-01'
  assert util.getPreviousYmd('2000-01-01', 1) == '1999-12-31'
  assert util.getPreviousYmd('2000-01-01', 365) == '1999-01-01'
  assert util.getPreviousYmd('2000-01-01', 366) == '1998-12-31'

