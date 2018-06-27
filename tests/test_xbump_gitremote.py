#!/usr/bin/python
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

from unittest import TestCase, main

from mock import patch

from xintegtools.xbump.gitremote import GitRemote


class GitRemoteTester(TestCase):

    repository = {'proto': 'git', 'uri': 'gitsrv:genbox/overlay_base', 'branch': 'master'}
    tags = {
        'my-profile-1.2.3': '5ec2e91120c6380977ff6f021820c4ef368e388c',
        'my-profile-1.2.4': '1d993a6d5f8670ec227dc5d270f2037f941c9c95',
        'my-profile-extra-1.2.4-r1': '0da1b1516fddf1b2faf659018c513869f87184b0',
        'my-profile-2.0.0': '036050e4b47d426d9d5fe65f67e4b57ef8687385'
    }
    branches = {
        'master': '899e51d3d2b94b694dfc9976ee37e57d63d7829e',
        '1.0/rb': 'e55c2bb004bb47fd96c1e636ddf9c81272b191e0',
        '2.0/rb': '5345705804277d31277687bb312fb136e2a95725',
        '2.1/rb': '3d860d7504bb51f9306288aa822d8b17c74b4038',
        'wip-79234_board_foobar': 'dbddd0cb22c3fad79ac29ebac70a85cc18619746'
    }

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_tag_exists(self, mock_cmd):
        hg = GitRemote({'proto': 'mercurial'})
        self.assertFalse(hg.tag_exists('my-profile-1.2.3'))

        git = GitRemote(self.repository)

        data = str()
        mock_cmd.return_value = (data, str())
        self.assertFalse(git.tag_exists(str()))
        for tag, sha1 in self.tags.iteritems():
            data = '%s\t\trefs/tags/%s\n' % (sha1, tag)
            mock_cmd.return_value = (data, str())
            self.assertTrue(git.tag_exists(tag))

        mock_cmd.return_value = (str(), str())
        self.assertFalse(git.tag_exists('my-profile-2.0.0'))

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_resolve_tag(self, mock_cmd):
        hg = GitRemote({'proto': 'mercurial'})
        self.assertEqual(hg.resolve_tag('my-profile-1.2.3'), str())

        git = GitRemote(self.repository)

        data = str()
        mock_cmd.return_value = (data, str())
        self.assertEqual(git.resolve_tag(str()), str())
        for tag, sha1 in self.tags.items():
            data = '%s\t\trefs/tags/%s\n' % (self.tags[tag], tag)
            mock_cmd.return_value = (data, str())
            self.assertEqual(git.resolve_tag(tag), sha1)

        mock_cmd.return_value = (str(), str())
        self.assertEqual(git.resolve_tag('my-profile-extra-1.2.4-r1'), str())

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_resolve_tags(self, mock_cmd):
        hg = GitRemote({'proto': 'mercurial'})
        self.assertEqual(hg.resolve_tags(), dict())

        git = GitRemote(self.repository)

        data = str()
        for tag, sha1 in self.tags.items():
            data += '%s\t\trefs/tags/%s\n' % (sha1, tag)
        mock_cmd.return_value = (data, str())
        self.assertEqual(git.resolve_tags(), self.tags)

        mock_cmd.return_value = (str(), str())
        self.assertEqual(git.resolve_tags(), dict())

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_get_tag_from_sha1(self, mock_cmd):
        git = GitRemote(self.repository)

        data = str()
        for tag, sha1 in self.tags.items():
            data += '%s\t\trefs/tags/%s\n' % (sha1, tag)
        mock_cmd.return_value = (data, str())
        for tag, sha1 in self.tags.items():
            self.assertEqual(git.get_tag_from_sha1(sha1), tag)
        self.assertEqual(git.get_tag_from_sha1('0' * 41), str())
        self.assertEqual(git.get_tag_from_sha1('899e51d3d2b94b694dfc8976ee37e57d63d7829e'), str())

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_branch_exists(self, mock_cmd):
        hg = GitRemote({'proto': 'mercurial'})
        self.assertFalse(hg.tag_exists('master'))

        git = GitRemote(self.repository)

        data = str()
        mock_cmd.return_value = (data, str())
        self.assertFalse(git.branch_exists(str()))
        for branch, sha1 in self.branches.iteritems():
            data = '%s\t\trefs/heads/%s\n' % (sha1, branch)
            mock_cmd.return_value = (data, str())
            self.assertTrue(git.branch_exists(branch))

        mock_cmd.return_value = (str(), str())
        self.assertFalse(git.branch_exists('my-profile-2.0.0'))

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_resolve_branch(self, mock_cmd):
        hg = GitRemote({'proto': 'mercurial'})
        self.assertEqual(hg.resolve_branch('master'), str())

        git = GitRemote(self.repository)

        data = str()
        mock_cmd.return_value = (data, str())
        self.assertEqual(git.resolve_branch(str()), str())
        for branch, sha1 in self.branches.items():
            data = '%s\t\trefs/heads/%s\n' % (self.branches[branch], branch)
            mock_cmd.return_value = (data, str())
            self.assertEqual(git.resolve_branch(branch), sha1)

        mock_cmd.return_value = (str(), str())
        self.assertEqual(git.resolve_branch('1.0/rb'), str())

    @patch('xintegtools.xbump.gitremote.GitRemote._run_cmd')
    def test_resolve_branches(self, mock_cmd):
        hg = GitRemote({'proto': 'mercurial'})
        self.assertEqual(hg.resolve_branches(), dict())

        git = GitRemote(self.repository)

        data = str()
        for branch, sha1 in self.branches.items():
            data += '%s\t\trefs/heads/%s\n' % (sha1, branch)
        mock_cmd.return_value = (data, str())
        self.assertEqual(git.resolve_branches(), self.branches)

        mock_cmd.return_value = (str(), str())
        self.assertEqual(git.resolve_branches(), dict())


if __name__ == '__main__':
    main()
