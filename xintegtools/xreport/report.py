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

import os
import re

from consts import VDB_PATH

from package import XPackage

from report_utils import readfile


class XReport(object):
    _dir_filters = [re.compile('^/var/db/pkg')]

    def __init__(self, root=None, portage_configroot=None):
        self.vdb = None
        self.vdb_collisions = None
        self.vdb_processed = None
        self.vdb_orphans = None
        self.filelist = None
        if root is None:
            self.root = '/'
        else:
            self.root = os.path.abspath(root)
        if portage_configroot is None:
            self.portage_configroot = '/'
        else:
            self.portage_configroot = os.path.abspath(portage_configroot)

    def _vdb_load_pkg(self, arg, dirname, fnames):
        if not 'CONTENTS' in fnames:
            return
        name = os.path.basename(dirname)
        cat = readfile(dirname + '/CATEGORY', True).strip()

        if not name + '.ebuild' in fnames:
            return

        self.vdb.append(XPackage(dirname, cat, name))

    def _filelist_filter(self, arg, dirname, fnames):
        if dirname.startswith(self.root):
            dirname = dirname[len(self.root):]
            if len(dirname) == 0 or dirname[0] != '/':
                dirname = '/' + dirname
        for filter in self._dir_filters:
            if filter.search(dirname):
                while len(fnames):
                    del fnames[0]
                return

        def _normalize_path(mypath):
            """
            os.path.normpath("//foo") returns "//foo" instead of "/foo"
            We dislike this behavior so we create our own normpath func
            to fix it.
            """
            if mypath.startswith(os.path.sep):
                # posixpath.normpath collapses 3 or more leading slashes to just 1.
                return os.path.normpath(2 * os.path.sep + mypath)
            else:
                return os.path.normpath(mypath)

        for file in fnames:
            fullname = _normalize_path('%s/%s' % (dirname, file))
            if not os.path.isdir(self.root + fullname):
                self.filelist[fullname] = True

    def vdb_create(self):
        if self.vdb is not None:
            del self.vdb
        self.vdb = []
        os.path.walk(self.root + VDB_PATH, self._vdb_load_pkg, None)
        self.vdb.sort(lambda x, y: cmp(x.name, y.name))

    def filelist_create(self):
        if self.filelist is not None:
            del self.filelist
        self.filelist = {}

        os.path.walk(self.root, self._filelist_filter, None)

    def vdb_check(self, info_func=None):
        if self.vdb is None:
            self.vdb_create()

        nb_iter = len(self.vdb)

        if self.vdb_processed:
            del self.vdb_processed
        self.vdb_processed = {}

        if self.vdb_collisions:
            del self.vdb_collisions
        self.vdb_collisions = {}

        collisions = []

        for pkg_num, pkg in enumerate(self.vdb):
            ret = 0
            if info_func is not None:
                info_func(pkg_num + 1, nb_iter)
            for file in pkg.pkgfiles:
                if file.check(self.root):
                    ret += 1
                # collision check
                if file.type != 'dir':
                    if file.name in self.vdb_processed:
                        if file.name not in collisions:
                            collisions.append(file.name)
                        self.vdb_processed[file.name].append(pkg.name)
                    else:
                        self.vdb_processed[file.name] = [pkg.name]
            pkg.res = ret
        # Create collision list
        for file in collisions:
            self.vdb_collisions[file] = self.vdb_processed[file]

    def find_orphans(self, info_func=None):
        # Create orphan list
        if self.filelist is None:
            self.filelist_create()
        if self.vdb_processed is None:
            self.vdb_check()

        nb_iter = len(self.filelist)

        if self.vdb_orphans:
            del self.vdb_orphans
        self.vdb_orphans = {}
        for file_num, file in enumerate(self.filelist):
            info_func(file_num + 1, nb_iter)
            if file not in self.vdb_processed:
                self.vdb_orphans[file] = True
