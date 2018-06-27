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

import subprocess

from xintegtools.xbump.utils import error, warning, is_git_sha1


class GitRemote(object):
    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    def _run_cmd(cmd):
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
            error(output)
        return output, ''

    def tag_exists(self, tag):
        """ Return True if tag exists else False.
        """
        if self.repository['proto'] != 'git':
            warning('%s repositories are currently not supported.' % self.repository['proto'])
            return False
        if not tag:
            return False
        cmd = ['git', 'ls-remote', '--tags', self.repository['uri'], tag]
        stdoutdata, _ = self._run_cmd(cmd)
        if stdoutdata and stdoutdata.strip().endswith(tag):
            return True
        return False

    def resolve_tag(self, tag):
        """ Return the SHA1 of the tag
        """
        if self.repository['proto'] != 'git':
            warning('%s repositories are currently not supported.' % self.repository['proto'])
            return str()
        if not tag:
            warning('Try to resolve empty tag')
            return str()
        cmd = ['git', 'ls-remote', '--tags', self.repository['uri'], tag]
        stdoutdata, _ = self._run_cmd(cmd)
        if stdoutdata and stdoutdata.strip().endswith(tag):
            return stdoutdata[:40]
        return str()

    def resolve_tags(self):
        """ Return a dict in the form {'tag_name': 'SHA1'}
        """
        tags = dict()
        if self.repository['proto'] != 'git':
            warning('%s repositories are currently not supported.' % self.repository['proto'])
            return tags
        cmd = ['git', 'ls-remote', '--tags', self.repository['uri']]
        stdoutdata, _ = self._run_cmd(cmd)
        if stdoutdata:
            for line in stdoutdata.splitlines():
                tags[line.split('refs/tags/')[-1]] = line[:40]
        return tags

    def get_tag_from_sha1(self, sha1):
        """ Return tag name associated to SHA1 or empty string
        """
        if not is_git_sha1(sha1):
            error('%s is not a valid SHA1' % sha1)
            return str()
        tags = self.resolve_tags()
        for tag, rev in tags.items():
            if rev == sha1:
                return tag
        return str()

    def branch_exists(self, branch=str()):
        """ Return True if branch exists else False.
        """
        if self.repository['proto'] != 'git':
            warning('%s repositories are currently not supported.' % self.repository['proto'])
            return False
        if not branch:
            branch = self.repository['branch']
            if not branch:
                return False
        cmd = ['git', 'ls-remote', '--heads', self.repository['uri'], branch]
        stdoutdata, _ = self._run_cmd(cmd)
        if stdoutdata and stdoutdata.strip().endswith(branch):
            return True
        return False

    def resolve_branch(self, branch=str()):
        """ Return the SHA1 of the HEAD of the branch
        """
        if self.repository['proto'] != 'git':
            warning('%s repositories are currently not supported.' % self.repository['proto'])
            return str()
        if not branch:
            branch = self.repository['branch']
            if not branch:
                return str()
        cmd = ['git', 'ls-remote', '--heads', self.repository['uri'], branch]
        stdoutdata, _ = self._run_cmd(cmd)
        if stdoutdata and stdoutdata.strip().endswith(branch):
            return stdoutdata[:40]
        return str()

    def resolve_branches(self):
        """ Return a dict in the form {'branch_name': 'SHA1'}
        """
        branches = dict()
        if self.repository['proto'] != 'git':
            warning('%s repositories are currently not supported.' % self.repository['proto'])
            return branches
        cmd = ['git', 'ls-remote', '--heads', self.repository['uri']]
        stdoutdata, _ = self._run_cmd(cmd)
        if stdoutdata:
            for line in stdoutdata.splitlines():
                branches[line.split('refs/heads/')[-1]] = line[:40]
        return branches
