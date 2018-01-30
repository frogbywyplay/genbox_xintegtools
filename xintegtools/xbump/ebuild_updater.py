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

from ebuild import Ebuild
from gitremote import GitRemote
from target_ebuild import TargetEbuildContent
from utils import error, info, warning, is_git_sha1

from re import compile


class TargetEbuildUpdater(object):
    def __init__(self, ebuild, verbose=False):
        self.verbose = verbose
        self.template = Ebuild(ebuild, verbose=verbose)
        f = open(self.template.abspath)
        self.data = TargetEbuildContent(f.read())
        f.close()
        repo_info = {'uri': self.data.uri, 'branch': self.data.branch, 'proto': 'git'}
        self.git = GitRemote(repo_info)

    def is_target_ebuild(self):
        if 'target-r' in self.template.inherited:
            return True
        return False

    def update_branch(self, branch):
        if not branch:
            return False
        if not self.git.branch_exists(branch):
            error('Unkonwn branch %s for repository %s' % (branch, self.data.uri))
            return False
        if branch != self.data.branch:
            try:
                self.data.branch = branch
            except ValueError, e:
                error(e.message)
                return False
        return True

    def update_revision(self, revision):
        sha1 = str()
        if revision == 'HEAD':
            sha1 = self.git.resolve_branch()
        elif not is_git_sha1(revision):
            sha1 = self.git.resolve_tag(revision)
        else:
            sha1 = revision

        if not sha1:
            return False
        tag = self.git.get_tag_from_sha1(sha1)
        if tag:
            if self.verbose: info('SHA1 %s is tagged as %s' % (sha1, tag))
        else:
            if self.verbose: error('No tag associated to SHA1 %s' % sha1)
            return False

        if sha1 != self.data.commit:
            try:
                self.data.commit = sha1
            except ValueError, e:
                error(e.message)
                return False
        return True

    def update_overlays(self, overlays=str()):
        overlays_to_update = dict()
        for overlay in overlays.split(','):
            if not overlay: continue
            [name, revision] = overlay.split(':')
            if name in self.data.overlays.keys():
                # TODO: check revision exists in overlay for concerned branch
                if not is_git_sha1(revision):
                    warning('Skip invalid revision %s for overlay %s.' % (revision, name))
                    continue
                overlays_to_update[name] = revision
            else:
                warning('Skip unknown overlay %s (not found in %s).' % (name, self.template.abspath))
        for name, spec in self.data.overlays.items():
            overlay_revision = str()
            if name in overlays_to_update.keys():
                overlay_revision = overlays_to_update[name]
            else:
                overlay_revision = GitRemote(spec).resolve_branch()
            if not overlay_revision:
                error('Unable to resolve HEAD for branch %s from overlay %s' % (spec['branch'], name))
                continue
            try:
                self.data.overlays = {name: overlay_revision}
                if self.verbose: info('Update overlay %s from %s to %s' % (name, spec['revision'], overlay_revision))
            except ValueError, e:
                error(e.message)
        return True

    def compute_version(self, use_tag=False, version=str()):
        my_version = str()
        origin = str()
        ver_regexp = compile('(\d+)((\.\d+)*)')
        repo_info = {'uri': self.data.uri, 'branch': self.data.branch, 'proto': 'git'}
        if use_tag:
            origin = 'latest tag on branch %s' % repo_info['branch']
            tag = self.git.get_tag_from_sha1(self.data.commit)
            my_version = ver_regexp.search(tag).group()
        elif version:
            origin = 'command line version argument'
            my_version = ver_regexp.search(version).group()
        else:
            origin = 'template ebuild version'
            num_regexp = compile('\d+')
            old_version = ver_regexp.search(self.template.version).group()
            splitted_version = num_regexp.findall(old_version)
            splitted_version[-1] = str(int(splitted_version[-1]) + 1)
            my_version = '.'.join(splitted_version)
        if self.verbose: info('Version computed from %s: %s.' % (origin, my_version))
        return my_version

    def release_ebuild(self, version, force=False):
        if not version:
            return str()
        filename = '%s/%s/%s/%s-%s.ebuild' % (
            self.template.overlay, self.template.category, self.template.name, self.template.name, version
        )
        if self.data.write_into(filename, force):
            return filename
        return str()
