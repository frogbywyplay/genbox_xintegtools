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

from utils import InvalidArgument, error, info

from portage import db, root, settings
from portage.exception import InvalidAtom
from portage.versions import catpkgsplit

class Ebuild(object):

    def __init__(self, atom, verbose = False):
        self.verbose = verbose
        self.cpv = self.__best_match(atom)
        if not self.cpv:
            raise InvalidArgument('No match for atom %s.' % atom)
        elif self.verbose:
            info('Use %s as template to create new target ebuild.' % self.cpv)
        (self._abspath, self._overlay) = self.portage_db.findname2(self.cpv)

    def __best_match(self, atom):
        settings.unlock()
        settings['ACCEPT_KEYWORDS'] = '*'
        settings.lock()

        self.portage_db = db[root]["porttree"].dbapi
        try:
            return self.portage_db.xmatch('bestmatch-visible', atom)
        except InvalidAtom:
            error('%s is not a valid atom.' % atom)
            raise InvalidArgument('Invalid atom %s.' % atom)

    def __get(self, value):
        return self.portage_db.aux_get(self.cpv, [value], self._overlay)[0]

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

