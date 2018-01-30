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

import sys


class XReportOutput(object):
    def __init__(self, errors_only=False, contents=False):
        self.errors_only = errors_only
        self.contents = contents

    def _header(self, output_file):
        pass

    def _footer(self, output_file):
        pass

    def _package(self, pkg, output_file):
        pass

    def _collisions(self, collisions, output_file):
        pass

    def _orphans(self, orphans, output_file):
        pass

    def process(self, report, output_file=sys.stdout):
        self._header(output_file)
        for pkg in report.vdb:
            self._package(pkg, output_file)

        if report.vdb_collisions and len(report.vdb_collisions):
            self._collisions(report.vdb_collisions, output_file)

        if report.vdb_orphans and len(report.vdb_orphans):
            self._orphans(report.vdb_orphans, output_file)
        self._footer(output_file)


class XCompareOutput(object):
    def __init__(self):
        pass

    def process(self, comapre, output_file=sys.stdout):
        pass
