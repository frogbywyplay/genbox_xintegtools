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
from __future__ import absolute_import

import sys

from xutils import color, info, is_verbose, die

from xintegtools.xreport.output import XReportOutput, XCompareOutput


class XReportTXTOutput(XReportOutput):
    def __init__(self, errors_only=False, contents=False):
        XReportOutput.__init__(self, errors_only, contents)

    def _header(self, output_file):
        info('Target VDB report', output=output_file)
        print >> output_file, ''

    def _package(self, pkg, output_file, _):
        total_files = len(pkg.pkgfiles)
        if self.errors_only and pkg.res == total_files:
            return
        info('%s/%s' % (pkg.cat, pkg.name), output=output_file)
        if pkg.res == total_files:
            res_str = color.green('%i/%i' % (pkg.res, total_files))
        else:
            res_str = color.yellow('%i/%i' % (pkg.res, total_files))
        print >> output_file, '   Checked: %s files' % res_str
        if pkg.res != total_files:
            for file_ in pkg.pkgfiles:
                if file_.status:
                    for error in file_.status:
                        if error == 'EMTIME':
                            out_str = '%s: %s' % (color.red('MTIME'), file_.name)
                            if is_verbose():
                                out_str += " (recorded '%i'!= actual '%i')" % (file_.mtime, file_.status['EMTIME'])
                        elif error == 'ECHKSUM':
                            out_str = '%s: %s' % (color.red('MD5-DIGEST'), file_.name)
                            if is_verbose():
                                out_str += " (recorded '%s'!= actual '%s')" % (file_.md5sum, file_.status['ECHKSUM'])
                        elif error == 'ENOENT':
                            out_str = '%s: %s' % (color.red('AFK'), file_.name)
                        else:
                            out_str = '%s: %s' % (color.red('UNKNOWN'), file_.name)
                        print >> output_file, '   ' + out_str
        print >> output_file, ''

    def _collisions(self, collisions, output_file):
        info('Packages file collision', output=output_file)
        for file_ in collisions:
            out_str = '   %s:' % file_
            for pkg in collisions[file_]:
                out_str += ' %s' % pkg
            print >> output_file, out_str
        print >> output_file, ''

    def _orphans(self, orphans, output_file):
        info('Orphan files ' + color.yellow('(%i)' % len(orphans)), output=output_file)
        for orphan in orphans:
            print >> output_file, '   %s' % orphan


class XCompareTXTOutput(XCompareOutput):
    def __init__(self):
        XCompareOutput.__init__(self)

    @staticmethod
    def _process_version(old, new):
        if old:
            if new:
                return '    Update: %s -> %s\n' % (color.blue(old), color.green(new))
            return '    Removed: %s\n' % (color.red(old))
        elif new:
            return '    New: %s\n' % (color.green(new))
        else:
            pass
        return ''

    @staticmethod
    def _get_flag(use, type_, val):
        if val != '1':
            use = '-%s' % use
        if type_ == 'new':
            return color.yellow(use) + '%'
        elif type_ == 'mod':
            if val == '1':
                return color.red(use)
            return color.blue(use)
        elif type_ == 'rem':
            return '(%s)' % color.yellow(use)
        return None

    def _process_flags(self, flags):
        if not flags:
            return ''
        out_str = '    Flags:'
        for use, val in flags.iteritems():
            out_str += ' %s' % self._get_flag(use, val[0], val[1])
        return out_str + '\n'

    def process(self, compare, output_file=sys.stdout):
        info('Target comparison: %s -> %s' % (compare.old, compare.new),\
             output=output_file)
        print >> output_file, ''
        for pkg_id, pkg in compare.pkg_diff.iteritems():
            pkg_name = pkg_id.rsplit(':', 1)
            if pkg_name is None:
                die('Internal error when parsing comparison results')
            out_str = pkg_name[0]
            if pkg_name[1] != 'None':
                out_str += '(%s)\n' % pkg_name[1]
            else:
                out_str += '\n'
            out_str += self._process_version(pkg.get('old'), pkg.get('new'))
            out_str += self._process_flags(pkg.get('use'))
            info(out_str, output=output_file)
