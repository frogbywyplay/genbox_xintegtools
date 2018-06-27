#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2016 Wyplay, All Rights Reserved.
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

import re
import os

from xintegtools.xbump.utils import error


class TargetEbuildContent(object):

    # expand is used to reference ': ${var:=value}' construction
    # quote is used to reference possible quote around value
    VAR_REGEXP = r'^\s*(?P<expand>:\s+\${)?(?P<var>%s)(?(expand):)?=(?P<quote>")?(?P<value>(?:[^"]|\.)*)(?(quote)")(?(expand)})\s*(?:#.*)?$'  # pylint: disable=line-too-long

    def __init__(self, data):
        self.data = data
        self._uri = None
        self._branch = None
        self._commit = None
        self._overlays = None

    def __extract(self, variable):
        for line in self.data.splitlines():
            my_match = re.match(self.VAR_REGEXP % variable, line)
            if my_match:
                return my_match.group('value')
        return str()

    def __extract_overlays(self):
        available_overlays = list()
        for line in self.data.splitlines():
            my_match = re.match(self.VAR_REGEXP % r'XOV_\w+_URI', line)
            if my_match:
                var = my_match.group('var')
                available_overlays += [var[var.find('_') + 1:var.rfind('_')].lower().replace('_', '-')]
        return available_overlays

    def __inject(self, variable, value, after=None):
        varregex = self.VAR_REGEXP % variable
        if after:
            lines = self.data.splitlines()
            # first remove 'XOV_TOTO_REVISION=""'
            try:
                lines.pop(next(idx for idx, line in enumerate(lines) if re.match(varregex, line)))
            except StopIteration:
                pass

            # then append it after `after`
            aftervarregex = self.VAR_REGEXP % after
            try:
                lines.insert(
                    next(idx for idx, line in enumerate(lines) if re.match(aftervarregex, line)) + 1,
                    '%s="%s"' % (variable, value)
                )
            except StopIteration:
                return False
            self.data = '\n'.join(lines)
            return True
        else:
            for line in self.data.splitlines():
                my_match = re.match(varregex, line)
                if my_match:
                    my_line = re.sub(my_match.group('value'), value, line)
                    self.data = self.data.replace(line, my_line)
                    return True
        return False

    @property
    def uri(self):
        if self._uri is None:
            self._uri = self.__extract('EGIT_REPO_URI')
        return self._uri

    @uri.setter
    def uri(self, value):
        if not self.__inject('EGIT_REPO_URI', value):
            raise ValueError('Unable to set EGIT_REPO_URI to %s' % value)
        self._uri = value

    @property
    def branch(self):
        if self._branch is None:
            self._branch = self.__extract('EGIT_BRANCH')
        return self._branch

    @branch.setter
    def branch(self, value):
        if not self.__inject('EGIT_BRANCH', value, after='EGIT_REPO_URI'):
            raise ValueError('Unable to set EGIT_BRANCH to %s' % value)
        self._branch = value

    @property
    def commit(self):
        if self._commit is None:
            self._commit = self.__extract('EGIT_COMMIT')
        return self._commit

    @commit.setter
    def commit(self, value):
        if not self.__inject('EGIT_COMMIT', value, after='EGIT_REPO_URI'):
            raise ValueError('Unable to set EGIT_COMMIT to %s.' % value)
        self._commit = value

    @property
    def overlays(self):
        if self._overlays is None:
            self._overlays = dict()
            for ov in self.__extract_overlays():
                ovvar = ov.upper().replace('-', '_')
                self._overlays[ov] = {
                    'uri': self.__extract('XOV_%s_URI' % ovvar),
                    'branch': self.__extract('XOV_%s_BRANCH' % ovvar),
                    'revision': self.__extract('XOV_%s_REVISION' % ovvar),
                    'proto': self.__extract('XOV_%s_PROTO' % ovvar)
                }
        return self._overlays

    @overlays.setter
    def overlays(self, value):
        variable = 'XOV_%s_REVISION'
        for overlay, revision in value.iteritems():
            var_overlay = overlay.upper().replace('-', '_')
            if not self.__inject(variable % var_overlay, revision, after='XOV_%s_URI' % var_overlay):
                raise ValueError('Unable to set %s to %s.' % (variable % var_overlay, revision))
            self._overlays[overlay]['revision'] = revision

    def write_into(self, filename, force=False):
        if os.path.exists(filename) and not force:
            error('Filename %s already exists.' % filename)
            return False
        try:
            with open(filename, 'w') as f:
                f.write(self.data)
        except IOError, e:
            error('%s: %s' % (filename, e.strerror))
            return False
        return True
