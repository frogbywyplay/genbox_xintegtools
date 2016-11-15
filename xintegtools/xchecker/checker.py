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
from utils import error

from os.path import exists
from re import match
from subprocess import Popen, PIPE
from urlparse import urlparse

def getTargetPackages(set = 'world', full = True):
    """ This method is equivalent to run the following shell command to get list of all target packages
        which would be installed:
        xmerge --pretend --quiet --columns --color=n world 2> /dev/null | sed -n "/ to /p" | awk '{print $2}'
        Note: '--nocheck' is required to avoid an infinite loop.
    """
    xmerge_pkg_cmd = ['xmerge', '--pretend', '--quiet', '--columns', '--color=n', set]
    if full: xmerge_pkg_cmd.insert(-1, '--emptytree')
    p = Popen(xmerge_pkg_cmd, stdout=PIPE, stderr=open('/dev/null', 'w'))
    (out, err) = p.communicate()

    target_pkg = dict()
    if not out.split('\n')[0]:
        error('The following command failed to complete successfully: %s' % ' '.join(xmerge_pkg_cmd) )
        error('Results will be inaccurate or false.')
        return target_pkg
    for line in out.split('\n'):
        if ' to ' in line and not line.startswith(' * '):
            array = line[6:].strip().split(' ')
            pkg = array[0]
            version = array[1]
            if pkg.startswith('product-targets'):
                continue
            target_pkg[pkg] = version
    return target_pkg

class ProfileChecker(object):

    def __init__(self, target = 'current'):
        self.__profile = ProfileParser(target)

    def has_loop(self):
        profile_directories = self.__profile.stack()
        if len(set(profile_directories)) == len(profile_directories):
            return False
        return True

    def packages(self):
        """ Return a dict with the following keys:
            * extra: list atom present in packages but not installed
            * missing: list atom not present in packages but installed
            * version: list atom with a given version in packages but installed at another.
                       dict in the form: 'atom': (version in packages, installed version)
        """
        packages_report = {'extra': list(), 'missing': list(), 'version': dict()}
        for package, version in self.__profile.packages.items():
            try:
                ebuild = Ebuild(package)
                ebuild_version = '%s-r%d' % (ebuild.version, ebuild.revision) if ebuild.revision > 0 else ebuild.version
                if version != ebuild_version:
                    packages_report['version'][package] = (version, ebuild.version)
            except InvalidArgument:
                packages_report['extra'] += [package]
        for package, version in getTargetPackages().items():
            if package not in self.__profile.packages.keys():
                packages_report['missing'] += [package]
        return packages_report

    def virtuals(self):
        """ Return a dict with the following keys:
            * provide: list atom who should provide a virtual but does not set PROVIDE in ebuild.
                       dict in the form 'virtual': 'atom'
            * unknown: list atom present in virtuals but without installable ebuilds.
        """
        virtuals_report = {'provide': dict(), 'unknown': list()}
        for virtual, depend in self.__profile.virtuals.items():
            try:
                ebuild = Ebuild(depend)
                if not ebuild.provide or virtual != ebuild.provide:
                    virtuals_report['provide'][virtual] = depend
            except InvalidArgument:
                virtuals_report['unknown'] += [depend]
        return virtuals_report

class EbuildChecker(object):

    group_whitelist = ['common', 'frogbywyplay', 'generic', 'tools', 'web']
    mainline_branch = '^master$'
    stable_branch = '^((\d+\.){2,}\d+)(-stable)$'
    wip_branch = '^wip-C?\d{1,6}_?[\w.-]*$'

    def __init__(self, ebuild, profile):
        self.ebuild = ebuild
        with open(ebuild.abspath) as my_ebuild:
            self.buffer = BufferParser(my_ebuild.readlines())
            my_ebuild.close()
        self.profile = profile

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

    def is_wip_git_branch(self):
        my_branch = self.buffer.get_variable('EGIT_BRANCH')
        if match(self.wip_branch, my_branch):
            return True
        return False

    def is_valid_git_group(self, current_group):
        my_group = self.buffer.get_variable('EGIT_GROUP')
        group_whitelist = self.group_whitelist + current_group
        if my_group not in group_whitelist:
            return False
        return True

    def is_git_template(self):
        if self.buffer.get_variable('EGIT_REV') == "" and self.buffer.get_variable('EGIT_REVISION') == "":
            return False
        return True

    def uris(self):
        hosts = list()
        my_restrict = self.ebuild.restrict

        if 'mirror' in my_restrict or 'primaryuri' in my_restrict:
            hosts += self.src_uri_hostnames()
            return hosts
        elif 'fetch' in my_restrict:
            # nothing to check
            return hosts
        else:
            # GENTOO_MIRRORS + SRC_URI
            for mirror in self.profile.gentoo_mirrors.split():
                hosts += [urlparse(mirror).hostname]
            hosts += self.src_uri_hostnames()
            return hosts

    def src_uri_hostnames(self):
        re_mirror = r'^mirror://(?P<mirror>\w[\w.-]*)/.*'
        my_uri = self.ebuild.src_uri

        if not my_uri or my_uri is None:
            return list()

        mirror_match = match(re_mirror, my_uri)
        if mirror_match:
            return self.expand_mirror_hostname(mirror_match.group('mirror'))
        else:
            return [urlparse(my_uri).hostname]

    def expand_mirror_hostname(self, mirror):
        # parse thirdpartymirrors files to get mirror
        expanded_mirror = list()

        try:
            mirror_list = self.profile.thirdpartymirrors[mirror]
        except KeyError:
            return expanded_mirror

        for mirror in mirror_list:
            expanded_mirror += [urlparse(mirror).hostname]
        return expanded_mirror

    def scan_filesdir(self):
        import magic
        from os import stat, walk
        from os.path import dirname

        # mimetype dict is of type: mime -> list of filename
        # size dict is of type: filename -> size in bytes
        filesdir_map = {'mimetype': dict(),
                        'size': dict()}
        filesdir = '%s/files' % dirname(self.ebuild.abspath)

        mime_guess = magic.open(magic.MAGIC_MIME)
        mime_guess.load()
        for dirname, sudbirlist, filelist in walk(filesdir):
            for file in filelist:
                my_file = '%s/%s' % (dirname, file)
                mimetype = mime_guess.file(my_file)
                if mimetype:
                    if mimetype in my_map.keys():
                        filesdir_map['mimetype'][mimetype] += [my_file]
                    else:
                        filesdir_map['mimetype'][mimetype] = [my_file]
                size = stat(my_file).st_size
                if size > 20 * 1024 * 1024:
                    filesdir_map['size'][my_file] = size
        return filesdir_map

