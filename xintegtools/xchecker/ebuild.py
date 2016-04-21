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

from utils import error, info

from portage import create_trees
from portage_exception import InvalidAtom
from portage_versions import catpkgsplit
from os import getenv
from os.path import basename

class InvalidArgument(ValueError):
    pass

class Ebuild(object):

    def __init__(self, atom, target = True, verbose = False):
        self.verbose = verbose
        my_root = '/usr/targets/%s/root/' % getenv('CURRENT_TARGET', 'current') if target else '/'
        my_trees = create_trees(config_root = my_root, target_root = my_root)
        self.portage_db = my_trees[my_root]['porttree'].dbapi
        try:
            self.cpv = self.portage_db.xmatch('bestmatch-visible', atom)
        except InvalidAtom:
            if verbose: error('%s is not a valid atom.' % atom)
            raise InvalidArgument('Invalid atom %s.' % atom)
        if not self.cpv:
            raise InvalidArgument('No match for atom %s.' % atom)
        (self._abspath, self._overlay) = self.portage_db.findname2(self.cpv)

    def __get(self, value):
        return self.portage_db.aux_get(self.cpv, [value], self._overlay)[0]

    def __str__(self):
        return '%s::%s' % (self.cpv, basename(self._overlay))

    @property
    def category(self):
        return catpkgsplit(self.cpv)[0]

    @property
    def name(self):
        return catpkgsplit(self.cpv)[1]

    @property
    def version(self):
        return catpkgsplit(self.cpv)[2]

    @property
    def revision(self):
        my_cpv = catpkgsplit(self.cpv)
        return int(0) if len(my_cpv) == 3 else int(my_cpv[3][1:])

    @property
    def abspath(self):
        return self._abspath

    @property
    def overlay(self):
        return self._overlay

    @property
    def inherited(self):
        return self.__get('INHERITED')

    @property
    def iuse(self):
        return self.__get('IUSE')

    @property
    def keywords(self):
        return self.__get('KEYWORDS')

    @property
    def license(self):
        return self.__get('LICENSE')

    @property
    def depend(self):
        return self.__get('DEPEND')

    @property
    def rdepend(self):
        return self.__get('RDEPEND')

    @property
    def eapi(self):
        return self.__get('EAPI')

    @property
    def provide(self):
        return self.__get('PROVIDE')

    @property
    def src_uri(self):
        return self.__get('SRC_URI')

    @property
    def restrict(self):
        return self.__get('RESTRICT')

