#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import os, re, sys

from xutils import color, die, warn, info, vinfo, is_verbose, XUtilsError
from report import XReport
from compare import XCompare
from consts import *

class XReportCmdline(XReport):
        """ xreport command line tool class. """
        def __init__(self, root=None, portage_configroot=None):
                self.prog_cnt = 0
                try:
                        XReport.__init__(self, root, portage_configroot)
                except XUtilsError, e:
                        die(str(e))

        def check_progress(self, curr, total):
                if not is_verbose():
                        return
                curr = curr * 100 / total
                for i in range(self.prog_cnt):
                        sys.stdout.write("\b")
                prog_str = " %3i%% " % curr
                self.prog_cnt = len(prog_str)
                sys.stdout.write(prog_str)
                sys.stdout.flush()

        def end_progress(self):
                self.prog_cnt = 0
                if is_verbose():
                        print

        def vdb_create(self):
                try:
                        vinfo("Building vdb ...")
                        XReport.vdb_create(self)
                except XUtilsError, e:
                        die(str(e))

        def vdb_check(self):
                try:
                        vinfo("Building file list ...")
                        XReport.filelist_create(self)
                        vinfo("Checking packages ...", eol=False)
                        XReport.vdb_check(self, self.check_progress)
                        self.end_progress()
                        vinfo("Checking for orphans ...", eol=False)
                        XReport.find_orphans(self, self.check_progress)
                        self.end_progress()

                except XUtilsError, e:
                        die(str(e))

class XCompareCmdline(XCompare):
        """ xcompare command line too class. """
        def __init__(self, old, new):
                XCompare.__init__(self, old, new)

        def compare(self):
		try:
	                vinfo("Loading %s ..." % self.old)
        	        self.old_db = self._load(self.old)
                	vinfo("Loading %s ..." % self.new)
	                self.new_db = self._load(self.new)
        	        vinfo("Building package databases")
                	XCompare.gen_db(self)
	                vinfo("Starting comparison")
        	        XCompare.compare(self)
		except XUtilsError, e:
			die(str(e))

