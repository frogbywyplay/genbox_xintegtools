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

from portage.output import colorize

def error(text):
    error = colorize('red', '* Error:')
    text = colorize('bold', text)
    print('%s %s' % (error, text))

def warning(text):
    warning = colorize('yellow', '* Warning:')
    text = colorize('bold', text)
    print('%s %s' % (warning, text))

def info(text):
    info = colorize('green', '* Info:')
    text = colorize('bold', text)
    print('%s %s' % (info, text))

class InvalidArgument(ValueError):
    pass

def is_git_sha1(sha1):
    '''Tests if the value could be a SHA1.'''
    if not isinstance(sha1, str): return False
    l = len(sha1)
    # 'man git-rev-parse', --short: ... The minimum length is 4.
    if l < 4 or l > 40: return False
    for i in sha1:
        if i not in "0123456789abcdef": return False
    return True

