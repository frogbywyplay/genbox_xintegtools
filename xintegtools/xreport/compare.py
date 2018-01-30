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

import exceptions

from xml.sax import handler, make_parser

from xutils import XUtilsError

from errno import ENOENT


class packageParser(handler.ContentHandler):
    def __init__(self):
        handler.ContentHandler.__init__(self)
        self.db = {}
        self.current = None
        self.setState(self.defaultStart, None)

    def clear(self):
        self.db = {}
        self.current = None
        self.setState(self.defaultStart, None)

    def setState(self, start, end):
        if start:
            self.startElement = start
        else:
            self.startElement = lambda a, b: None
        if end:
            self.endElement = end
        else:
            self.endElement = lambda a: None

    def defaultStart(self, name, attrs):
        if name == 'package':
            self.current = {
                'name': attrs.get('name'),
                'version': attrs.get('version'),
                'category': attrs.get('category'),
                'slot': attrs.get('slot'),
            }
            self.setState(self.pkgProcess, self.pkgEnd)

    def defaultEnd(self, name):
        self.setState(self.defaultStart, None)

    def pkgProcess(self, name, attrs):
        if name == 'use_flags':
            self.flags = {}
            self.setState(self.useStart, self.pkgEnd)

    def pkgEnd(self, name):
        if name == 'package':
            self.db['%s/%s:%s' % (self.current['category'], self.current['name'], self.current['slot'])] = self.current
            self.current = None
            self.setState(self.defaultStart, self.pkgEnd)
        elif name == 'use_flags':
            self.current['flags'] = self.flags
            self.flags = None
            self.setState(self.pkgProcess, self.pkgEnd)

    def useStart(self, name, attrs):
        if name == 'use':
            self.flags[attrs.get('name')] = attrs.get('val', '0')


class XCompare(object):
    """ Class to compare two xml report documents. """

    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.old_db = self.new_db = None
        self.parser = make_parser()
        self.pkgParser = None

    def _load(self, filename):
        if not self.pkgParser:
            self.pkgParser = packageParser()
            self.parser.setContentHandler(self.pkgParser)
        else:
            self.pkgParser.clear()
        try:
            self.parser.parse(filename)
        except IOError, e:
            if e.errno == ENOENT:
                raise XUtilsError("Can't find \"%s\"" % filename)
            else:
                raise e
        return self.pkgParser.db

    def gen_db(self):
        if not self.old_db:
            self.old_db = self._load(self.old)
        if not self.new_db:
            self.new_db = self._load(self.new)

        self.pkgParser = None

    def _compare_flags(self, old_flags, new_flags):
        flags = {}
        if not (old_flags or new_flags):
            return None
        elif not old_flags:
            for use, val in new_flags.iteritems():
                flags[use] = ('new', val)
            return flags
        elif not new_flags:
            for use, val in old_flags.iteritems():
                flags[use] = ('rem', val)
            return flags
        else:
            for use, val in new_flags.iteritems():
                old_val = old_flags.pop(use, None)
                if not old_val:
                    flags[use] = ('new', val)
                elif old_val != val:
                    flags[use] = ('mod', val)
            for use, val in old_flags.iteritems():
                flags[use] = ('rem', val)
            return flags

    def compare(self):
        if not self.old_db or \
           not self.new_db:
            self.gen_db()

        self.pkg_diff = {}

        for pkg_id, old_pkg in self.old_db.iteritems():
            new_pkg = self.new_db.pop(pkg_id, None)
            if new_pkg:
                if old_pkg.get('version') != new_pkg.get('version'):
                    self.pkg_diff[pkg_id] = {'old': old_pkg.get('version'), 'new': new_pkg.get('version')}
                use_diff = self._compare_flags(old_pkg.get('flags'), new_pkg.get('flags'))
                if use_diff:
                    if not self.pkg_diff.get(pkg_id):
                        self.pkg_diff[pkg_id] = {}
                    self.pkg_diff[pkg_id]['use'] = use_diff
            else:
                self.pkg_diff[pkg_id] = {'old': old_pkg.get('version')}

        self.old_db = None
        for pkg_id, new_pkg in self.new_db.iteritems():
            self.pkg_diff[pkg_id] = {'new': new_pkg.get('version')}

        return self.pkg_diff
