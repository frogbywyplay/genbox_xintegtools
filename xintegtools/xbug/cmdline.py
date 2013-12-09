#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import os, re, sys

from xutils import color, die, warn, info, vinfo, is_verbose
from xbug import XBug, XBugError

class XBugCmdline(XBug):
        """ xbug command line tool class. """
        def __init__(self):
                self.prog_cnt = 0
                try:
                        XBug.__init__(self)
                except XBugError, e:
                        die(str(e))

        def parse(self, infile):
                XBug.parse(self, infile)
                vinfo("%i Bugs found" % len(self.bugs))
        
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

        def query_db(self):
                vinfo("Querying bugzilla ...", eol=False)
                total_bugs = len(self.bugs)

                for i, bug in enumerate(self.bugs):
                        self.check_progress(i, total_bugs)
                        try:
                                self.bugs[bug] = XBug.query_db(self, bug)
                        except XBugError, e:
                                if is_verbose():
                                        print
                                warn(str(e))
                self.end_progress()

