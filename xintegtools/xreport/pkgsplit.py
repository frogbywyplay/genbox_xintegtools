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

try:
    from portage.versions import pkgsplit
except:
    import re

    ver_regexp = re.compile('^(cvs\\.)?(\\d+)((\\.\\d+)*)([a-z]?)((_(pre|p|beta|alpha|rc)\\d*)*)(-r(\\d+))?$')

    def ververify(myver, silent=1):
        if ver_regexp.match(myver):
            return 1
        else:
            return 0

    def pkgsplit(mypkg, silent=1):
        myparts = mypkg.split('-')

        if len(myparts) < 2:
            return None
        for x in myparts:
            if len(x) == 0:
                return None

        #verify rev
        revok = 0
        myrev = myparts[-1]
        if len(myrev) and myrev[0] == 'r':
            try:
                int(myrev[1:])
                revok = 1
            except ValueError:  # from int()
                pass
        if revok:
            verPos = -2
            revision = myparts[-1]
        else:
            verPos = -1
            revision = 'r0'

        if ververify(myparts[verPos]):
            if len(myparts) == (-1 * verPos):
                return None
            else:
                for x in myparts[:verPos]:
                    if ververify(x):
                        return None
                        #names can't have versiony looking parts
                myval = ['-'.join(myparts[:verPos]), myparts[verPos], revision]
                return myval[:]
        else:
            return None
