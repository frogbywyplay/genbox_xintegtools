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

from __future__ import print_function

import string

from portage.output import colorize


def error(text):
    error_ = colorize('red', '* Error:')
    text = colorize('bold', text)
    print('%s %s' % (error_, text))


def warning(text):
    warning_ = colorize('yellow', '* Warning:')
    text = colorize('bold', text)
    print('%s %s' % (warning_, text))


def info(text):
    info_ = colorize('green', '* Info:')
    text = colorize('bold', text)
    print('%s %s' % (info_, text))


class InvalidArgument(ValueError):
    pass


def is_git_sha1(sha1):
    '''Tests if the value could be a SHA1.'''
    return isinstance(sha1, str) and (4 < len(sha1) <= 40) and all(i in string.hexdigits for i in sha1)
