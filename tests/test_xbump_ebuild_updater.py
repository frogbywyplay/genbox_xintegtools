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

from mock import MagicMock, patch
from os.path import dirname, realpath
from sys import modules, path
from unittest import TestCase, main

path.insert(0, realpath(dirname(modules[__name__].__file__) + '/..'))
from xintegtools.xbump.ebuild_updater import TargetEbuildUpdater


class TargetEbuildUpdaterTester(TestCase):
    @patch('xintegtools.xbump.ebuild_updater.GitRemote')
    @patch('xintegtools.xbump.ebuild_updater.TargetEbuildContent')
    @patch('xintegtools.xbump.ebuild_updater.Ebuild')
    @patch('xintegtools.xbump.ebuild_updater.open')
    def test_is_target_ebuild(self, mock_open, mock_ebuild, mock_targetebuildcontent, mock_git):
        mock_open.return_value = MagicMock(spec=file)

        updater = TargetEbuildUpdater('mock')
        mock_ebuild.inherited.return_value = 'git-r3 eutils toolchain-funcs multilib'
        self.assertFalse(updater.is_target_ebuild())

        mock_ebuild.inherited.return_value = 'git-r3 eutils target-r1 overlays'
        self.assertFalse(updater.is_target_ebuild())

    @patch('xintegtools.xbump.ebuild_updater.GitRemote')
    @patch('xintegtools.xbump.ebuild_updater.TargetEbuildContent')
    @patch('xintegtools.xbump.ebuild_updater.Ebuild')
    @patch('xintegtools.xbump.ebuild_updater.open')
    def test_update_branch(self, mock_open, mock_ebuild, mock_targetebuildcontent, mock_git):
        mock_open.return_value = MagicMock(spec=file)

        updater = TargetEbuildUpdater('mock')
        self.assertFalse(updater.update_branch(str()))

        mock_git.return_value.branch_exists.return_value = False
        self.assertFalse(updater.update_branch('master'))

        mock_git.return_value.branch_exists.return_value = True
        mock_targetebuildcontent.branch.return_value = 'master'
        self.assertTrue(updater.update_branch('master'))

        mock_targetebuildcontent.branch.side_effect = ValueError('mock')
        self.assertTrue(updater.update_branch('1.5/rb'))

    @patch('xintegtools.xbump.ebuild_updater.GitRemote')
    @patch('xintegtools.xbump.ebuild_updater.TargetEbuildContent')
    @patch('xintegtools.xbump.ebuild_updater.Ebuild')
    @patch('xintegtools.xbump.ebuild_updater.open')
    def test_update_revision(self, mock_open, mock_ebuild, mock_targetebuildcontent, mock_git):
        mock_open.return_value = MagicMock(spec=file)

        updater = TargetEbuildUpdater('mock')
        mock_git.return_value.resolve_branch.return_value = str()
        self.assertFalse(updater.update_revision('HEAD'))

        mock_git.return_value.resolve_branch.return_value = 'bad0' * 10
        mock_git.return_value.get_tag_from_sha1.return_value = str()
        self.assertFalse(updater.update_revision('HEAD'))

        mock_git.return_value.get_tag_from_sha1.return_value = '2.5.1'
        mock_targetebuildcontent.commit.return_value = 'bad0' * 10
        self.assertTrue(updater.update_revision('HEAD'))

        mock_targetebuildcontent.commit.return_value = 'bad1' * 10
        self.assertTrue(updater.update_revision('HEAD'))

        #mock_targetebuildcontent.return_value.commit.side_effect = ['bad1' * 10, ValueError('mock')]
        #self.assertFalse(updater.update_revision('HEAD'))

    @patch('xintegtools.xbump.ebuild_updater.GitRemote')
    @patch('xintegtools.xbump.ebuild_updater.TargetEbuildContent')
    @patch('xintegtools.xbump.ebuild_updater.Ebuild')
    @patch('xintegtools.xbump.ebuild_updater.open')
    def test_update_overlays(self, mock_open, mock_ebuild, mock_targetebuildcontent, mock_git):
        mock_open.return_value = MagicMock(spec=file)

        updater = TargetEbuildUpdater('mock')
        self.assertTrue(updater.update_overlays(str()))

        overlays = 'foo:899e51d3d2b94b694dfc9976ee37e57d63d7829e,bar:7f8ac3a7e773e09fb591e3b34f057c16d15c80e9'
        mock_targetebuildcontent.return_value.overlays.keys.return_value = ['foo', 'bar', 'base', 'board']
        mock_git.return_value.resolve_branch.return_value = 'a' * 40
        self.assertTrue(updater.update_overlays(overlays))

    @patch('xintegtools.xbump.ebuild_updater.GitRemote')
    @patch('xintegtools.xbump.ebuild_updater.TargetEbuildContent')
    @patch('xintegtools.xbump.ebuild_updater.Ebuild')
    @patch('xintegtools.xbump.ebuild_updater.open')
    def test_compute_revision(self, mock_open, mock_ebuild, mock_targetebuildcontent, mock_git):
        pass

    @patch('xintegtools.xbump.ebuild_updater.GitRemote')
    @patch('xintegtools.xbump.ebuild_updater.TargetEbuildContent')
    @patch('xintegtools.xbump.ebuild_updater.Ebuild')
    @patch('xintegtools.xbump.ebuild_updater.open')
    def test_release_ebuild(self, mock_open, mock_ebuild, mock_targetebuildcontent, mock_git):
        mock_open.return_value = MagicMock(spec=file)
        mock_targetebuildcontent.return_value.write_into.return_value = True
        mock_ebuild.return_value.overlay.return_value = '/var/lib/layman/targets'
        mock_ebuild.return_value.category.return_value = 'product-targets'
        mock_ebuild.return_value.name.return_value = 'frog'

        updater = TargetEbuildUpdater('mock')
        self.assertEqual(updater.release_ebuild(str()), str())

        version = '3.6.9'
        #self.assertEqual(updater.release_ebuild(version), '%s/%s/%s/%s-%s.ebuild' % (mock_ebuild.return_value.overlay.return_value, mock_ebuild.return_value.category.return_value, mock_ebuild.return_value.name.return_value, mock_ebuild.return_value.name.return_value, version))

        mock_targetebuildcontent.return_value.write_into.return_value = False
        self.assertEqual(updater.release_ebuild(version), str())


if __name__ == '__main__':
    main()
