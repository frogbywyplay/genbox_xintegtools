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

import sys, os

from xutils import color, info, is_verbose, die

from output import XBugOutput

from consts import *


class XBugTXTOutput(XBugOutput):
    def __init__(self):
        XBugOutput.__init__(self)

    def _color_status(self, status):
        if status == 'RESOLVED' or status == 'VERIFIED':
            return color.green(status)
        elif status == 'NEW' or status == 'ASSIGNED':
            return color.red(status)
        else:
            return status

    def _sort_bugs(self, bugs):
        def weight(a, bugs):
            wt = {'NEW': 5, 'ASSIGNED': 4, 'RESOLVED': 3, 'VERIFIED': 2}
            return wt.get(bugs[a].get('status'), 0)

        def compare(a, b, bugs):
            wa = weight(a, bugs)
            wb = weight(b, bugs)
            if wa > wb:
                return -1
            elif wa == wb:
                return 0
            else:
                return 1

        bug_ids = bugs.keys()
        bug_ids.sort(lambda a, b: compare(a, b, bugs))
        return bug_ids

    def process(self, xbug, ofile, full=False):
        bug_ids = self._sort_bugs(xbug.bugs)
        for bug_id in bug_ids:
            bug = xbug.bugs[bug_id]

            info('#%-14s : %-20s' % \
                    (
                     str(bug_id),
                     self._color_status(bug.get('status', '???'))
                    ))

            if full:
                print '    %-15s: %-40s' % ('url', '%s/show_bug.cgi?id=%i' % (BUGZILLA_URL, bug_id))
                print '    %-15s: %-40s' % ('summary', bug.get('summary', ''))
                print '    %-15s: %-20s' % ('resolution', bug.get('resolution', 'none'))
                print '    %-15s: %-10s' % ('milestone', bug.get('milestone', 'none'))
                print
