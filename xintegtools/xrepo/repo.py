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
from exceptions import Exception

XREPO_DATA_PATH = "/usr/share/xintegtools/xrepo"
XREPO_LICENSES_PATH = XREPO_DATA_PATH + "/licenses"
XREPO_ARCH_LIST_PATH = XREPO_DATA_PATH + "/arch.list"

class XrepoError(Exception):
        def __init__(self, num=0, msg=None, log=None):
                self.num = num
                self.msg = msg
                self.log = log

        def __str__(self):
                return self.msg

        def get_num(self):
                return self.num

        def get_log(self):
                return self.log

        def get_msg(self):
                return self.msg

class Xrepo(object):
        def __init__(self):
                self.dir = None

        def __cp(self, src, dest):
                fd_in = open(src, 'r')
                fd_out = open(dest, 'w')
                while 1:
                        buf = fd_in.read(4096)
                        if not buf:
                                break
                        fd_out.write(buf)
                fd_in.close()
                fd_out.close()

        def create(self, dest_dir):
                self.dir = os.path.abspath(dest_dir)
                if not os.path.exists(self.dir):
                        os.makedirs(self.dir)
                elif not os.path.isdir(self.dir):
                        raise XrepoError(num=1, msg="%s is not a directory" % dest_dir)

                os.chdir(self.dir)
                for dir in [ 'profiles', 'licenses', 'eclass' ]:
                        if not os.path.isdir(dir):
                                os.mkdir(dir)

                for file in [ 'profiles/use.local.desc', 'profiles/profiles.desc' ]:
                        fd = open(file, 'w')
                        fd.close()
                
                if os.path.isdir(XREPO_LICENSES_PATH):
                        for file in os.listdir(XREPO_LICENSES_PATH):
                                file_path = XREPO_LICENSES_PATH + '/' + file
                                if os.path.isfile(file_path):
                                        self.__cp(file_path, 'licenses/%s' % os.path.basename(file))
                if os.path.isfile(XREPO_ARCH_LIST_PATH):
                        self.__cp(XREPO_ARCH_LIST_PATH, 'profiles/arch.list')

