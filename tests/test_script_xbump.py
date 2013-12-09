#!/usr/bin/python
#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import unittest
import os, sys

curr_path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

sys.path.insert(0, curr_path + '/..')

class xbumpTester(unittest.TestCase):
        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

        def testHelp(self):
                self.failUnlessEqual(os.system('PYTHONPATH=%s/../ %s/../scripts/xbump --help' % (self.path, self.path)), 0)


if __name__ == "__main__":
        unittest.main()

