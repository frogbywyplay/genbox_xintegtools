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

from xintegtools.xbump import Ebuild

import mock
import unittest

class EbuildTester(unittest.TestCase):

    @mock.patch.object('portage.versions', )
    def test_category(self, mock_catpkgsplit):
        zlib = Ebuild('zlib')
        self.assertEqual(zlib.category, 'sys-libs', 'Bad category for zlib: %s' % zlib.category)
        mock_catpkgsplit.assert_called_with('sys-libs/zlib')

    def test_name(self):
        pass

    def test_version(self):
        pass

    def test_revision(self):
        pass

    def test_abspath(self):
        pass

    def test_overlay(self):
        pass

    def test_inherited(self):
        pass

    def test_iuse(self):
        pass

    def test_keywords(self):
        pass

    def test_license(self):
        pass

    def test_depend(self):
        pass

    def test_rdepend(self):
        pass

    def test_eapi(self):
        pass

if __name__ == "__main__":
    unittest.main()
