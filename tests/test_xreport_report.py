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

ROOT_DATA = curr_path + '/test_data/root-test.tar.gz'

XR_WORKDIR = curr_path + '/xr_workdir'

class xreportTester(unittest.TestCase):
        def __init__(self, methodName='runTest'):
                unittest.TestCase.__init__(self, methodName)
                self.path = os.path.realpath(os.path.dirname(sys.modules[__name__].__file__))

        def setUp(self):
                if not os.path.exists(ROOT_DATA):
			return
                if not os.path.exists(XR_WORKDIR):
                        os.makedirs(XR_WORKDIR)
                os.system('tar xfzp %s -C %s' % (ROOT_DATA, XR_WORKDIR))
                verbose(True)

        def testReport(self):
                if not os.path.exists(ROOT_DATA):
			self.fail('%s is missing: skipping test' % ROOT_DATA)
			return
                rep = c.XReportCmdline(root=XR_WORKDIR + '/root')
                out = o.XReportXMLOutput(errors_only=False)
                rep.vdb_create()
                out.process(rep, XR_WORKDIR + '/test.xml')
                self.failUnlessEqual(os.system("xmllint --noout --relaxng %s/../relax-ng/full.rng %s/test.xml"% (self.path, XR_WORKDIR)), 0)

        def testLicenses(self):
                if not os.path.exists(ROOT_DATA):
			self.fail('%s is missing: skipping test' % ROOT_DATA)
			return
                rep = c.XReportCmdline(root=XR_WORKDIR + '/root')
                out = o.XReportXMLOutput(errors_only=False)
                rep.vdb_create()
                out.process(rep, XR_WORKDIR + '/test.xml')
                self.failUnless(os.system('[ $(xsltproc %s/xreport/licenses.xsl %s/test.xml) == \'GPL-2\' ]' % (self.path, XR_WORKDIR)) == 0)

                self.failUnless(os.system('[ $(xsltproc %s/xreport/licenses2.xsl %s/test.xml) == \'public\' ]' % (self.path, XR_WORKDIR)) == 0)
                self.failUnless(os.system('[ $(xsltproc %s/xreport/licenses3.xsl %s/test.xml) == \'True\' ]' % (self.path, XR_WORKDIR)) == 0)
                del rep
                
        def testHg(self):
                if not os.path.exists(ROOT_DATA):
			self.fail('%s is missing: skipping test' % ROOT_DATA)
			return
                rep = c.XReportCmdline(root=XR_WORKDIR + '/root')
                out = o.XReportXMLOutput(errors_only=False)
                rep.vdb_create()
                out.process(rep, XR_WORKDIR + '/test.xml')
                self.failUnless(os.system('[ $(xsltproc %s/xreport/scm_hg_uri.xsl %s/test.xml) == \'gui/wyvas/branch-3/branch-3.0\' ]' % (self.path, XR_WORKDIR)) == 0)
                self.failUnless(os.system('[ $(xsltproc %s/xreport/scm_hg_branch.xsl %s/test.xml) == \'rb-3.3\' ]' % (self.path, XR_WORKDIR)) == 0)
                self.failUnless(os.system('[ $(xsltproc %s/xreport/scm_hg_revision.xsl %s/test.xml) == \'901009aa4945\' ]' % (self.path, XR_WORKDIR)) == 0)
                del rep
                
        def testGit(self):
                if not os.path.exists(ROOT_DATA):
			self.fail('%s is missing: skipping test' % ROOT_DATA)
			return
                rep = c.XReportCmdline(root=XR_WORKDIR + '/root')
                out = o.XReportXMLOutput(errors_only=False)
                rep.vdb_create()
                out.process(rep, XR_WORKDIR + '/test.xml')
                self.failUnless(os.system('[ $(xsltproc %s/xreport/scm_git_uri.xsl %s/test.xml) == \'kernel-wyplay-brcm.git\' ]' % (self.path, XR_WORKDIR)) == 0)
                self.failUnless(os.system('[ $(xsltproc %s/xreport/scm_git_branch.xsl %s/test.xml) == \'2.6.37.6-brcm-2.8-isb8k\' ]' % (self.path, XR_WORKDIR)) == 0)
                self.failUnless(os.system('[ $(xsltproc %s/xreport/scm_git_revision.xsl %s/test.xml) == \'d409094\' ]' % (self.path, XR_WORKDIR)) == 0)
                del rep
        
        def tearDown(self):
                os.system('rm -rf %s/*' % XR_WORKDIR)
        
if __name__ == "__main__":
        unittest.main()

