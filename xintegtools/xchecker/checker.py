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
from __future__ import with_statement

from ebuild import Ebuild, InvalidArgument
from parser import BufferParser, ProfileParser
from utils import info, error

from re import match

class ProfileChecker(object):

    def __init__(self, target = 'current'):
        self.__profile = ProfileParser(target = 'current')

    def validate_profile(self):
        """Validate that packages and virtuals files are correctly managed.
        """
        info('Processing packages files.')
        for package, version in self.__profile.packages.items():
            try:
                ebuild = Ebuild(package)
                ebuild_version = '%s-r%d' % (ebuild.version, ebuild.revision) if ebuild.revision > 0 else ebuild.version
                if version != ebuild_version:
                    error('%s: expected version in packages: %s - installed version: %s' % (package, version, ebuild.version))
            except InvalidArgument:
                error('%s present in packages has no matching ebuild!' % package)

        info('Processing virtuals files.')
        for virtual, depend in self.__profile.virtuals.items():
            try:
                ebuild = Ebuild(depend)
                if not ebuild.provide or virtual != ebuild.provide:
                    error('%s: missing "PROVIDE=%s" in %s' % (depend, virtual, ebuild.abspath))
            except InvalidArgument:
                error('%s present in virtuals has no matching ebuild!' % depend)

        def compare_with_installed(self):
            # check world file before warn
            pass

class EbuildChecker(object):

    group_whitelist = ['frogbywyplay', 'generic', 'tools', 'web']
    mainline_branch = '^master$'
    stable_branch = '^((\d+.){2,}\d+)(-stable)$'
    wip_branch = '^wip-C?\d{1,6}_?[\w.-]*$'

    def __init__(self, ebuild):
        self.ebuild = ebuild
        with open(ebuild.abspath) as my_ebuild:
            self.buffer = BufferParser(my_ebuild.readlines())
            my_ebuild.close()

    def is_mercurial(self):
        if not 'mercurial' in self.ebuild.inherited:
            return False
        if self.buffer.get_variable('EHG_REPO_URI'):
            return True
        return False

    def is_git(self):
        if not 'git' in self.ebuild.inherited:
            return False
        if self.buffer.get_variable('EGIT_REPO_URI'):
            return True
        return False

    def is_valid_git_branch(self):
        my_branch = self.buffer.get_variable('EGIT_BRANCH')
        my_regexp = '%s|%s|%s' % (self.mainline_branch, self.stable_branch, self.wip_branch)
        if match(my_regexp, my_branch):
            return True
        return False

    def is_valid_git_group(self, current_group):
        my_group = self.buffer.get_variable('EGIT_GROUP')
        group_whitelist = self.group_whitelist + current_group
        if my_group not in group_whitelist:
            return False
        return True

    def is_valid_src_uri(self, domain):
        my_restrict = self.ebuild.restrict
        if not my_restrict:
            # check GENTOO_MIRRORS
            pass
        elif 'mirror' in my_restrict or 'primaryuri' in my_restrict:
            # just check SRC_URI
            pass
        elif 'fetch' in my_restrict:
            # nothing to check
            pass

    def check_src_uri(self):
        my_uri = self.ebuild.src_uri
        if not my_uri:
            return True
        if my_uri.startswith('mirror://'):
            #check 3rdpartymirror
            return True
        if domain in my_uri:
            return True
        return False

    def check_gentoo_mirrors(self):
        from os import getenv
        gentoo_mirrors = getenv('GENTOO_MIRRORS', str())

    def __expand_mirror(self, mirror):
        # parse thirdpartymirrors files to get mirror
        pass

    def scan_filesdir(self):
        pass

if __name__ == '__main__':
    p = ProfileParser()
    for package in p.packages:
        try:
            ebuild = Ebuild(package)
            checker = EbuildChecker(ebuild)
            if checker.is_mercurial():
                error('HG ebuild %s' % ebuild.abspath)
            elif checker.is_git():
                if not checker.is_valid_git_branch():
                    error('Invalid branch in %s' % ebuild.abspath)
                if not checker.is_valid_git_group(['r7', 'st-sdk2-g6']):
                    error('Invalid group in %s' % ebuild.abspath)
            elif not checker.is_valid_src_uri('packages.wyplay.int'):
                    error('Invalid SRC_URI in %s' % ebuild.abspath)
        except InvalidArgument:
            error('Skip unknow package %s' % package)
