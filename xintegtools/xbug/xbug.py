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

import os, exceptions, re
import xmlrpclib as xrpc

from consts import *


class XBugError(exceptions.Exception):
    """ Error class for XBug. """

    def __init__(self, error=None):
        self.error = error

    def __str__(self):
        if self.error is not None:
            return self.error
        else:
            return ''


class XBug(object):
    _bug_group_regex = re.compile(r"bugtraq:?\s*((?:\#?[0-9]+\,?\s*)+)")
    _bug_regex = re.compile(r"([0-9]+)")

    def __init__(self):
        self.bugs = None
        self.bugz_db = None

    def _parse_line(self, line):
        for bug_group in self._bug_group_regex.findall(line):
            for bug in self._bug_regex.findall(bug_group):
                self.bugs[int(bug)] = {}

    def parse(self, infile):
        if self.bugs:
            del self.bugs

        self.bugs = {}
        for line in infile.readlines():
            self._parse_line(line)

    def query_db(self, bug):
        if self.bugz_db is None:
            self.bugz_db = xrpc.ServerProxy(BUGZILLA_URL + '/xmlrpc.cgi')
        try:
            ret = self.bugz_db.Bug.get_bugs({'ids': [bug]})['bugs'][0]
        except xrpc.Fault, e:
            if e.faultCode == 101:  # Unkown bug
                raise XBugError(e.faultString)
            else:
                raise e
        return {
            'summary': ret['summary'],
            'status': ret['internals']['bug_status'],
            'resolution': ret['internals']['resolution'],
            'milestone': ret['internals']['target_milestone']
        }
