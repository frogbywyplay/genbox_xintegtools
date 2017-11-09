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
from checker import collisionChecker, EbuildChecker, ProfileChecker
from ebuild import Ebuild, InvalidArgument
from parser import ProfileParser
from utils import info, error, print_item, warning

from portage import create_trees
from re import finditer
from urlparse import urlparse

def validateProfile(target= 'current'):
    profile = ProfileChecker(target)
    if profile.has_loop():
        error('loop in the profile... Aborting else will report too many false positives.')
        return 1
    packages = profile.packages()
    if packages['missing']:
        info('The following packages are installed but are missing in "packages":')
        for missing in packages['missing']:
            print_item(missing)
    if packages['extra']:
        info('The following packages are not installed but are listed in "packages":')
        for extra in packages['extra']:
            print_item(extra)
    if packages['version']:
        info('The following packages are not installed at the expected version:')
        print_item('package\t\texpected version\tinstalled version')
        for package, version in packages['version'].items():
            print_item('%s: %s\t%s' % (package, version[0], version[1]))

    virtuals = profile.virtuals()
    if virtuals['provide']:
        info('The following packages do not set PROVIDE variable:')
        for virtual, depend in virtuals['provide'].items():
            print_item('%s: PROVIDE="%s"' % (depend, virtual))
    if virtuals['unknown']:
        info('The following packages are declared in virtuals, but without installable candidate:')
        for unknown in virtuals['unknown']:
            print_item(unknown)

    target_profile = ProfileParser(target)
    base_hostname = urlparse(target_profile.profile_config['BASE_MIRROR']).hostname
    for mirror in target_profile.gentoo_mirrors.split():
        if urlparse(mirror).hostname != base_hostname:
            error('The current profile is using an invalid mirror %s' % mirror)

    my_trees = create_trees(config_root = target_profile.root, target_root = target_profile.root)
    portage_db = my_trees[target_profile.root]['porttree'].dbapi
    if portage_db.getRepositoryPath('wyplay'):
        error('The profile is using banned wyplay overlay')

    overlays = list()
    for overlay in portage_db.getRepositories():
        overlays += [portage_db.getRepositoryPath(overlay)]
    collisions = collisionChecker(overlays)
    if collisions['warn']:
        warning('The following packages are in conflict (but same ebuild):')
        for (ebuild, overlays) in sorted(collisions['warn']):
            print_item('%s present in the following overlays: %s' % (ebuild, ', '.join(overlays)))
    if collisions['error']:
        error('The following ebuilds are in conflict (and ebuild differs):')
        for (ebuild, overlays) in sorted(collisions['error']):
            print_item('%s present in the following overlays: %s' % (ebuild, ', '.join(overlays)))
    return 0


def validateEbuild(atom, profile):

    def validateEbuildEAPI():
        def get_inherit_line():
            k = int(0)
            for line in ebuild_validator.buffer.data:
                k += 1
                if line.startswith('inherit'):
                    return k
            return -1
        eapi = int(ebuild.eapi)
        eapi_line = ebuild_validator.buffer.get_line('EAPI')
        inherit_line = get_inherit_line()
        if inherit_line > 0 and eapi_line > inherit_line:
            error('%s defines EAPI after "inherit" statement.' % ebuild)
        for flag in ebuild.iuse.split():
            if (flag[0] == '+' or flag[0] == '-') and eapi == 0:
                error('%s must set its EAPI to 1 (currently EAPI=0).' % ebuild)
                break

    def validateGitEbuild():
        if not ebuild_validator.is_valid_git_branch():
            branch = ebuild_validator.buffer.get_variable('EGIT_BRANCH')
            warning('%s does not comply with Wyplay SCMP rules for branch "%s".' % (ebuild, branch))
            if ebuild_validator.is_wip_git_branch():
                warning('%s is using a WIP branch.' % ebuild)
        if not ebuild_validator.is_valid_git_group():
            error('%s fetchs its source code in "generic" gitlab group.' % ebuild)
        if ebuild_validator.is_git_template():
            error('%s is a template ebuild (i.e. fetchs its source code on HEAD of its gitlab repository).' % (ebuild))

    def validateEbuildUris():
        hostnames = ebuild_validator.uris()
        servername = urlparse(profile.profile_config['BASE_MIRROR']).hostname
        for host in hostnames:
            if host != servername:
                if hostnames.index(host) == 0:
                    error('%s will fetch its source code on %s.' % (ebuild, host))
                else:
                    warning('%s may fetch its source code on %s.' % (ebuild, host))

    def validateEbuildDependSyntax():
        def parenthesis_matching(input):
            opening = [match.start() for match in finditer('\(', input)]
            closing = [match.start() for match in finditer('\)', input)]
            for occurence in opening:
                if occurence > 0:
                    if input[occurence - 1] != ' ':
                        return 1
                if input[occurence + 1] != ' ':
                    return 1
            for occurence in closing:
                if occurence < len(input) - 1:
                    if input[occurence + 1] != ' ':
                        return 1
                if input[occurence - 1] != ' ':
                    return 1
            return 0

        if parenthesis_matching(ebuild.depend) > 0:
            error('%s has parenthesis spacing errors in DEPEND variable.' % ebuild)
        if parenthesis_matching(ebuild.rdepend) > 0:
            error('%s has parenthesis spacing errors in RDEPEND variable.' % ebuild)

    try:
        ebuild = Ebuild(atom)
    except InvalidArgument, e:
        error(e.message)
        return 1
    info('Checking %s' % ebuild)
    ebuild_validator = EbuildChecker(ebuild, profile)
    validateEbuildEAPI()
    if not ebuild_validator.has_license():
        warning('%s has no LICENSE.' % ebuild)
    if ebuild_validator.is_mercurial():
        warning('%s fetchs its source code in a mercurial repository.' % ebuild)
        if ebuild_validator.is_mercurial_template():
            error('%s is a template ebuild (i.e. fetchs its source code on HEAD of its mercurial repository).' % (ebuild))
    elif ebuild_validator.is_git():
        validateGitEbuild()
    else:
        validateEbuildUris()
    validateEbuildDependSyntax()
