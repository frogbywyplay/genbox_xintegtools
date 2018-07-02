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

from mock import MagicMock, patch, mock_open

from xintegtools.xbump.target_ebuild import TargetEbuildContent


class TargetEbuildContentTester(TestCase):

    data = """# Header & copyright\nEAPI=5\n
inherit target-r1\n
LICENSE="Wyplay"\nSLOT="0"\nKEYWORDS="arm"\n
#EGIT_REPO_URI="gitsrv:deprecated_uri"
EGIT_REPO_URI="%(uri)s"
: ${EGIT_BRANCH:="%(branch)s"}
EGIT_COMMIT="%(commit)s"

XOV_BASE_PROTO=%(xov_base_proto)s
XOV_BASE_URI=%(xov_base_uri)s
XOV_BASE_BRANCH=%(xov_base_branch)s
XOV_BASE_REVISION=%(xov_base_revision)s

: ${XOV_BOARD_PROTO:="%(xov_base_proto)s"}
XOV_BOARD_URI=%(xov_board_uri)s
#XOV_BOARD_BRANCH=master
"""
    data_values = {
        'uri': str(),
        'branch': str(),
        'commit': str(),
        'xov_base_uri': str(),
        'xov_base_branch': str(),
        'xov_base_revision': str(),
        'xov_base_proto': str(),
        'xov_board_uri': str()
    }

    def test_uri(self):
        self.data_values['uri'] = 'gitsrv:genbox/profiles-project'
        other_uri = 'user@github.com:frogbywyplay/profiles'

        my_ebuild = TargetEbuildContent(self.data % self.data_values)
        self.assertEqual(my_ebuild.uri, self.data_values['uri'])
        my_ebuild.uri = other_uri
        self.assertEqual(my_ebuild.uri, other_uri)
        self.assertIn(other_uri, my_ebuild.data)

        other_data = 'EAPI=3\ninherit target-r1\nEGIT_BRANCH="master"\n\n#garbage data\n'
        other_ebuild = TargetEbuildContent(other_data)
        self.assertEqual(other_ebuild.uri, str())
        with self.assertRaisesRegexp(ValueError, 'Unable to set EGIT_REPO_URI to %s' % other_uri):
            other_ebuild.uri = other_uri

    def test_branch(self):
        self.data_values['branch'] = '1.2/rb'
        other_branch = 'wip-36152_new_board'

        my_ebuild = TargetEbuildContent(self.data % self.data_values)
        self.assertEqual(my_ebuild.branch, self.data_values['branch'])
        my_ebuild.branch = other_branch
        self.assertEqual(my_ebuild.branch, other_branch)
        self.assertIn(other_branch, my_ebuild.data)

        other_data = 'EGIT_REPO_URI="gitsrv:genbox/profiles"\nEAPI=1\n#garbage data\n'
        other_ebuild = TargetEbuildContent(other_data)
        self.assertEqual(other_ebuild.branch, str())
        other_ebuild.branch = other_branch
        self.assertEqual(other_ebuild.branch, other_branch)
        self.assertIn(other_branch, other_ebuild.data)

    def test_commit(self):
        self.data_values['commit'] = '0' * 40
        other_commit = 'f' * 40

        my_ebuild = TargetEbuildContent(self.data % self.data_values)
        self.assertEqual(my_ebuild.commit, self.data_values['commit'])
        my_ebuild.commit = other_commit
        self.assertEqual(my_ebuild.commit, other_commit)
        self.assertIn(other_commit, my_ebuild.data)

    def test_overlays(self):
        self.data_values['xov_base_proto'] = 'git'
        self.data_values['xov_base_uri'] = 'gitsrv:genbox/overlay_base'
        self.data_values['xov_board_uri'] = 'gitsrv:genbox/overlay_board'
        self.data_values['xov_base_branch'] = 'master'
        self.data_values['xov_base_revision'] = '12345abcde' * 4
        other_values = {'base': '0' * 40, 'board': 'f' * 40}

        my_ebuild = TargetEbuildContent(self.data % self.data_values)
        for value in ['uri', 'branch', 'proto', 'revision']:
            base_value = 'xov_base_%s' % value
            self.assertEqual(my_ebuild.overlays['base'][value], self.data_values[base_value])
        self.assertEqual(my_ebuild.overlays['board']['uri'], self.data_values['xov_board_uri'])
        my_ebuild.overlays = other_values
        self.assertEqual(my_ebuild.overlays['base']['revision'], other_values['base'])
        self.assertEqual(my_ebuild.overlays['base']['uri'], self.data_values['xov_base_uri'])
        self.assertEqual(my_ebuild.overlays['board']['revision'], other_values['board'])
        self.assertEqual(my_ebuild.overlays['board']['uri'], self.data_values['xov_board_uri'])
        for value in other_values.values():
            self.assertIn(value, my_ebuild.data)

    @patch('__builtin__.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_write_into(self, mock_exists, mock_open_):
        my_ebuild = TargetEbuildContent(self.data % self.data_values)

        mock_exists.return_value = True
        self.assertFalse(my_ebuild.write_into('mock', force=False))

        self.assertTrue(my_ebuild.write_into('mock', force=True))

        mock_exists.return_value = False
        mock_open_.side_effect = IOError(13)
        self.assertFalse(my_ebuild.write_into('mock'))


if __name__ == '__main__':
    main()
