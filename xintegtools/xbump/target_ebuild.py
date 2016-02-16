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

from utils import error

from os.path import exists
from re import match, sub

class TargetEbuildContent(object):

    # expand is used to reference ': ${var:=value}' construction
    # quote is used to reference possible quote around value
    VAR_REGEXP=r'^\s*(?P<expand>:\s+\${)?(?P<var>%s)(?(expand):)?=(?P<quote>\")?(?P<value>(?:[^\\"]|\\.)*)(?(quote)\")(?(expand)})\s*(?:#.*)?$'

    def __init__(self, data):
        self.data = data
        self._uri = None
        self._branch = None
        self._commit = None
        self._overlays = None

    def __extract(self, variable):
        for line in self.data.splitlines():
            my_match = match(self.VAR_REGEXP % variable, line)
            if my_match:
                return my_match.group('value')
        return str()

    def __extract_overlays(self):
        available_overlays = list()
        for line in self.data.splitlines():
            my_match = match(self.VAR_REGEXP % 'XOV_\w+_URI', line)
            if my_match:
                var = my_match.group('var')
                available_overlays += [var[var.find('_')+1:var.rfind('_')].lower().replace('_', '-')]
        return available_overlays

    def __inject(self, variable, value, after = None):
        for line in self.data.splitlines():
            my_match = match(self.VAR_REGEXP % variable, line)
            if my_match:
                my_line = sub(my_match.group('value'), value, line)
                self.data = self.data.replace(line, my_line)
                return True
        if after is not None:
            for line in self.data.splitlines():
                my_match = match(self.VAR_REGEXP % after, line)
                if my_match:
                    my_line = line + '\n%s=%s' % (variable, value)
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
        if not self.__inject('EGIT_BRANCH', value, after = 'EGIT_REPO_URI'):
            raise ValueError('Unable to set EGIT_BRANCH to %s' % value)
        self._branch = value

    @property
    def commit(self):
        if self._commit is None:
            self._commit = self.__extract('EGIT_COMMIT')
        return self._commit

    @commit.setter
    def commit(self, value):
        if not self.__inject('EGIT_COMMIT', value, after = 'EGIT_REPO_URI'):
            raise ValueError('Unable to set EGIT_COMMIT to %s.' % value)
        self._commit = value

    @property
    def overlays(self):
        if self._overlays is None:
            self._overlays = dict()
            for ov in self.__extract_overlays():
                self._overlays[ov] = {'uri': self.__extract('XOV_%s_URI' % ov.upper().replace('-','_')), 
                                      'branch': self.__extract('XOV_%s_BRANCH' % ov.upper().replace('-', '_')), 
                                      'revision': self.__extract('XOV_%s_REVISION' % ov.upper().replace('-', '_')),
                                      'proto': self.__extract('XOV_%s_PROTO' % ov.upper().replace('-', '_'))}
        return self._overlays

    @overlays.setter
    def overlays(self, value):
        variable = 'XOV_%s_REVISION'
        for overlay, revision in value.items():
            var_overlay = overlay.upper().replace('-', '_')
            if not self.__inject(variable % var_overlay, revision, after = 'XOV_%s_URI' % var_overlay):
                raise ValueError('Unable to set %s to %s.' % (variable % var_overlay, revision))
            self._overlays[overlay]['revision'] = revision

    def write_into(self, filename, force = False):
        if exists(filename) and not force:
            error('Filename %s already exists.' % filename)
            return False
        try:
            f = open(filename, 'w')
            f.write(self.data)
            f.close()
        except IOError, e:
            error('%s: %s' % (filename, e.strerror))
            return False
        return True
