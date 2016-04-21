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

from utils import error, warning

from os import getenv
from os.path import exists
from portage import config
from portage_const import INCREMENTALS
from portage_versions import pkgsplit
from re import compile, match

class ProfileParserWarning(Exception):
    pass

class ProfileParserError(Exception):
    pass

class ProfileParser(object):

    re_system = '(?P<system>\*)'
    re_minus = '(?P<minus>-)'
    re_operator = '(?P<operator>[<>]?=?)'
    re_depend = '(?P<depend>\w[\w-]*/\w[\w+-]*)'
    re_name = '(?P<name>\w[\w+-]*)'
    re_version = '(?P<version>(cvs\\.)?(\\d+)((\\.\\d+)*)([a-z]?)((_(pre|p|beta|alpha|rc)\\d*)*)(-r(\\d+))?)'
    re_comment = '(?P<comment>#.*)'

    def __init__(self, target = 'current'):
        root = '/' if target == 'host' else '/usr/targets/%s/root/' % getenv('CURRENT_TARGET', 'current')
        self.target = len(root) > 1
        self.profile_config = config(config_root = root, target_root = root, config_incrementals = INCREMENTALS)
        self.__packages = dict()
        self.__virtuals = dict()

    def __parse_file(self, filename, parser):
        for directory in self.profile_config.profiles:
            file = '%s/%s' % (directory, filename)
            if exists(file):
                f = open(file)
                lines = f.readlines()
                f.close()
                for line in lines:
                    if not line.strip():
                        continue
                    if line.startswith('#'):
                        continue
                    try:
                        parser(line.strip())
                    except ProfileParserWarning, e:
                        warning('%s: %s' % (file, e.message), prefix='ParserWarning')
                    except ProfileParserError, e:
                        error('%s: %s' % (file, e.message), prefix='ParserError')

    def stack(self):
        return self.profile_config.profiles

    @property
    def packages(self):
        def parse_algo(input):
            regexp = compile('^%s?%s?%s?%s(-%s)?\s*%s?$' % (self.re_minus, self.re_system, self.re_operator, self.re_depend, self.re_version, self.re_comment))
            matching = regexp.match(input)
            if matching:
                package_full = pkgsplit('%s-%s' % (matching.group('depend'), matching.group('version')) if matching.group('version') else matching.group('depend'))
                if package_full:
                    package = package_full[0]
                    version = '%s-%s' % (package_full[1], package_full[2]) if package_full[2] != 'r0' else package_full[1]
                else:
                    package = matching.group('depend')
                    version = str()
                if matching.group('minus'):
                    try:
                        if not version or version == self.__packages[package]:
                            del self.__packages[package]
                        else:
                            raise ProfileParserError('Try to remove %s but version mismatch: %s vs %s.' % (package, version, self.__packages[package]))
                    except KeyError:
                        raise ProfileParserError('Try to remove missing %s.' % package)
                elif matching.group('operator') == '=':
                    if not version:
                        raise ProfileParserWarning('Bad atom %s%s-%s' % (matching.group('operator'), package, version))
                    if package in self.__packages.keys():
                        previous_version = self.__packages[package]
                        self.__packages[package] = version
                        raise ProfileParserWarning('Overwrite package version for %s (%s -> %s).' % (package, previous_version, version))
                    self.__packages[package] = version
            else:
                raise ProfileParserError('Unmatched line: %s' % input)

        if not self.__packages:
            self.__parse_file('packages', parse_algo)
        return self.__packages

    @property
    def virtuals(self):
        def parse_algo(input):
            regexp = compile('^(?P<virtual>virtual/%s)\s+%s\s*%s?$' % (self.re_name, self.re_depend, self.re_comment))
            matching = regexp.match(input)
            if matching:
                virtual = matching.group('virtual')
                depend = matching.group('depend')
                if virtual in self.__virtuals.keys():
                    previous_depend = self.__virtuals[virtual]
                    self.__virtuals[virtual] = depend
                    raise ProfileParserWarning('Overwrite already provided %s (%s -> %s).' % (virtual, previous_depend, depend))
                self.__virtuals[virtual] = depend
            else:
                raise ProfileParserError('Unmatched line: %s' % input)

        if not self.__virtuals:
            self.__parse_file('virtuals', parse_algo)
        return self.__virtuals

    @property
    def gentoo_mirrors(self):
        return self.profile_config['GENTOO_MIRRORS']

    @property
    def thirdpartymirrors(self):
        return self.profile_config.thirdpartymirrors()

class BufferParser(object):

    assignation_regexp = r'^\s*(?P<expand>:\s+\${)?(?P<var>%s)(?(expand):)?=(?P<quote>\")?(?P<value>(?:[^\\"]|\\.)*)(?(quote)\")(?(expand)})\s*(?:#.*)?$'

    def __init__(self, buffer):
        self.data = buffer

    def get_variable(self, variable):
        for line in self.data:
            my_match = match(self.assignation_regexp % variable, line)
            if my_match:
                return my_match.group('value')
        return str()

    def get_line(self, variable):
        k = int(0)
        for line in self.data:
            k += 1
            my_match = match(self.assignation_regexp % variable, line)
            if my_match:
                return k
        return int(-1)
