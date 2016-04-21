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

from output import colorize

def error(text, prefix = 'Error'):
    error = colorize('red', '* %s:' % prefix)
    text = colorize('bold', text)
    print '%s %s' % (error, text)

def warning(text, prefix = 'Warning'):
    warning = colorize('yellow', '* %s:' % prefix)
    text = colorize('bold', text)
    print '%s %s' % (warning, text)

def info(text, prefix = 'Info'):
    info = colorize('green', '* %s:' % prefix)
    text = colorize('bold', text)
    print '%s %s' % (info, text)

def print_item(text):
    text = colorize('bold', '\t* %s' % text)
    print '%s' % text
