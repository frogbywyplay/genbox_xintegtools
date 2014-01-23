#!/usr/bin/python
#
# Copyright (C) 2006-2014 Wyplay, All Rights Reserved.
# This file is part of xintegtools.
# 
# xintegtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
# 
# xintegtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see file COPYING.
# If not, see <http://www.gnu.org/licenses/>.
#
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

