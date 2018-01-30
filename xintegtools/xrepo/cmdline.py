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

from xutils import warn, error, die, info

from repo import XrepoError, Xrepo


class XrepoCmdline(Xrepo):
    def __init__(self):
        Xrepo.__init__(self)

    def create(self, dest_dir):
        try:
            Xrepo.create(self, dest_dir)
        except XrepoError, e:
            die(str(e))
        info('Repository %s created' % os.path.basename(dest_dir))
