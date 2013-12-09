#!/usr/bin/python
#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import unittest
import sys, os, re

curr_path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

sys.path.insert(0, curr_path + '/..')

ROOT_DATA = curr_path + '/test_data/'

class xreportTester(unittest.TestCase):
        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

        def testCompare(self):
                if not os.path.exists(ROOT_DATA):
			self.fail('%s is missing: skipping test' % ROOT_DATA)
			return
                self.failUnlessEqual(os.system("xmllint --noout --relaxng %s/../relax-ng/compare/full.rng %s/compare.xml"% (self.path, ROOT_DATA)), 0)

if __name__ == "__main__":
        unittest.main()

