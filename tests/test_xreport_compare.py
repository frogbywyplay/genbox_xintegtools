#!/usr/bin/python
#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import unittest
import sys, os, re

curr_path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

sys.path.insert(0, curr_path + '/..')

import xintegtools.xreport.cmdline as c
import xintegtools.xreport.output_xml as o

from xutils import verbose

DATADIR = curr_path + '/test_data/'

XR_WORKDIR = curr_path + '/xr_workdir'

class xreportTester(unittest.TestCase):
        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

        def setUp(self):
		#self.skipTest('%s is missing.' % DATADIR) available from python2.7
                if not os.path.exists(XR_WORKDIR):
                        os.makedirs(XR_WORKDIR)
                verbose(True)

        def testCompare(self):
                if not os.path.exists(DATADIR):
			self.fail('%s is missing: skipping test' % DATADIR)
			return
                rep = c.XCompareCmdline(old=DATADIR + '/report1.xml', new=DATADIR + '/report2.xml')
                out = o.XCompareXMLOutput()
                rep.compare()
                out.process(rep, XR_WORKDIR + '/test.xml')
                self.failUnlessEqual(os.system("xmllint --noout --relaxng %s/../relax-ng/compare/full.rng %s/test.xml"% (self.path, XR_WORKDIR)), 0)

        def tearDown(self):
                os.system('rm -rf %s/*' % XR_WORKDIR)

if __name__ == "__main__":
        unittest.main()

