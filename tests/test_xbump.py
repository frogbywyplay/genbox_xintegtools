#!/usr/bin/python
#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import unittest
import sys, os, re

curr_path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

sys.path.insert(0, curr_path + '/..')
import xintegtools.xbump as b

XBUMP_TMP= curr_path + '/test_xbump'
XBUMP_UNKNOWN_EBUILD = XBUMP_TMP + '/unknown.ebuild'
XBUMP_NOSUCH_EBUILD = XBUMP_TMP + '/nosuch.ebuild'

class xbumpTester(unittest.TestCase):
        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

        def testErrorUpdateNoSuch(self):
                if not os.path.exists(XBUMP_TMP):
			self.fail('%s is missing: skipping test' % XBUMP_TMP)
			return
                xbump = b.Xbump()
                try:
                        xbump.update(XBUMP_NOSUCH_EBUILD)
                except b.XbumpError, e:
                        if e.msg != 'No such file':
                                raise e
                else:
                        raise 'an error should have been raised'
                del xbump

        def testErrorUpdateUnkown(self):
                if not os.path.exists(XBUMP_TMP):
			self.fail('%s is missing: skipping test' % XBUMP_TMP)
			return
                xbump = b.Xbump()
                try:
                        xbump.update(XBUMP_UNKNOWN_EBUILD)
                except b.XbumpError, e:
                        if e.msg != 'unknown ebuild type':
                                raise e
                else:
                        raise 'an error should have been raised'
                del xbump


if __name__ == "__main__":
        unittest.main()

