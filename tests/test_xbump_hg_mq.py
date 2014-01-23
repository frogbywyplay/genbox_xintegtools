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
import xintegtools.xbump as b

XBUMP_TMP= curr_path + '/test_xbump'
XBUMP_HG_MQ_EBUILD = XBUMP_TMP + '/portage-2.1.4.4.0.ebuild'
XBUMP_HG_MQ_NOTEMPLATE_EBUILD = XBUMP_TMP + '/portage-2.1.4.4.2_p2.ebuild'

class xbumpHG_MQTester(unittest.TestCase):
        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

        def testHG_MQUpdate(self):
                if not os.path.exists(XBUMP_TMP):
			self.fail('%s is missing: skipping test' % XBUMP_TMP)
			return
                xbump = b.Xbump()
                new_ebuild = xbump.update(XBUMP_HG_MQ_EBUILD, force=True)
                try:
                        new_ebuild = xbump.update(XBUMP_HG_MQ_EBUILD)
                except b.XbumpWarn:
                        pass
                new_ebuild = xbump.update(XBUMP_HG_MQ_EBUILD, force=True)
                os.unlink(XBUMP_TMP + '/' + new_ebuild + '.ebuild')
                new_ebuild = xbump.update(XBUMP_HG_MQ_EBUILD, force=False)
                os.unlink(XBUMP_TMP + '/' + new_ebuild + '.ebuild')
                del xbump

        def testHG_MQUpdateVersion(self):
                if not os.path.exists(XBUMP_TMP):
			self.fail('%s is missing: skipping test' % XBUMP_TMP)
			return
                xbump = b.Xbump()
                new_ebuild = xbump.update(XBUMP_HG_MQ_EBUILD, version='1', force=True)
                self.failUnless(re.match('.*\.1_p[0-9]+', new_ebuild),
                                '%s does not match \'.*\.1_p[0-9]+\'' % new_ebuild)
                os.unlink(XBUMP_TMP + '/' + new_ebuild + '.ebuild')

                new_ebuild = xbump.update(XBUMP_HG_MQ_EBUILD, version=['1', '1'], force=True)
                self.failUnless(re.match('.*\.1_p1', new_ebuild),
                                '%s does not match \'.*\.1_p1\'' % new_ebuild)
                os.unlink(XBUMP_TMP + '/' + new_ebuild + '.ebuild')
                del xbump

        def testHGUpdateNoTemplate(self):
                if not os.path.exists(XBUMP_TMP):
			self.fail('%s is missing: skipping test' % XBUMP_TMP)
			return
                xbump = b.Xbump()
                try:
                       new_ebuild = xbump.update(XBUMP_HG_MQ_NOTEMPLATE_EBUILD, force=True)
                except b.XbumpError, e:
                        if e.msg != 'Not a template':
                                raise e
                else:
                        raise 'An exception should have been raised'

if __name__ == "__main__":
        unittest.main()

