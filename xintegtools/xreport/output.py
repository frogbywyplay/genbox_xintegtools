#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
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

