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

import os, sys, exceptions, re
sys.path.insert(0, "/usr/lib/portage/pym")

from portage_versions import pkgsplit

from xutils.ebuild import ebuild_factory, XEbuild

from xutils import vinfo, is_verbose, XUtilsError

from consts import XBUMP_DEF_NAMING

def error_fmt(ebuild, type, msg=None):
        if ebuild.endswith(".ebuild"):
                ebuild = ebuild[:-7]
        out_str = "%-40s : %-5s" % (ebuild, type)
        if msg is not None:
                out_str += " (%s)" % msg
        return out_str

class XbumpError(exceptions.Exception):
        """ Error class for Xbump. """
        def __init__(self, ebuild, msg, log=None):
                self.ebuild = ebuild
                self.msg = msg
                self.log = log

        def __str__(self):
                return self.get_msg()

        def get_log(self):
                return self.log

        def get_msg(self):
                if self.msg is not None:
                        if self.ebuild is not None:
                                return error_fmt(self.ebuild, "ERROR", self.msg)
                        else:
                                return self.msg
                else:
                        return ""

class XbumpWarn(XbumpError):
        """ Warning class for Xbump """
        def __init__(self, ebuild, msg, log):
                XbumpError.__init__(self, ebuild, msg, log)

        def get_msg(self):
                if self.ebuild is not None and \
                   self.msg is not None:
                        return error_fmt(self.ebuild, "WARN", self.msg)
                else:
                        return ""

class Xbump(object):
        def __init__(self):
                return
        def update(self, file, version=None, force=False, name=XBUMP_DEF_NAMING):
                if not os.path.isfile(file):
                        raise XbumpError(file, "No such file")

                eb_scm = ebuild_factory(file)
                if eb_scm is None:
                        raise XbumpError(os.path.basename(file), 'unknown ebuild type')

                if not eb_scm.is_template():
                        raise XbumpError(os.path.basename(file), 'Not a template')

                if version is None:
                        try:
                                version = eb_scm.get_latest()
                        except XUtilsError, e:
                                raise XbumpError(eb_scm.get_name(), str(e), e.get_error_log())

                try:
                        eb_scm.set_version(version, True, name=name)
                except XUtilsError, e:
                        raise XbumpError(eb_scm.get_name(), str(e), e.get_error_log())

                try:
                        eb_scm.write(overwrite=force)
                except XUtilsError, e:
                        if e.num == 1:
                                raise XbumpWarn(eb_scm.get_name(), str(e), e.get_error_log())
                        else:
                                raise XbumpError(eb_scm.get_name(), str(e), e.get_error_log())
                if is_verbose():
                        print eb_scm.info()
                return eb_scm.get_name()

        def bump(self, file, delete=False, edit=False):
                if not os.path.isfile(file):
                        raise XbumpError(file, "No such file")

                eb = XEbuild(file)
                eb._read_file(file)
                old_name = eb.get_name()
                if edit:
                        editor = os.getenv("EDITOR", None)
                        if editor is None:
                                raise XbumpError(None, "Can't find editor, EDITOR envvar required")

                pkg_name = "%s-%s%s%s" % (eb.pn, ".".join(eb.pv['number']),
                                          eb.pv['letter'], eb.pv['suffix'])
                pkg_match = re.compile("^%s-r[0-9]+.ebuild$" % pkg_name)
                for eb_file in os.listdir(eb.path):
                        if pkg_match.match(eb_file):
                                file_split = pkgsplit(eb_file[:-7])
                                if eb.pr is None or \
                                   int(file_split[2][1:]) > int(eb.pr[1:]):
                                        eb.pr = file_split[2]

                if eb.pr:
                        eb.pr = 'r%i' % (int(eb.pr[1:]) + 1)
                else:
                        eb.pr = 'r1'

                vinfo("Bumping to %s" % eb.get_name())
                
                eb.write()

                if edit:
                        new_file = eb.path + eb.get_name() + ".ebuild"
                        cmd_ret = os.system("%s %s" % (editor, new_file))
                        if cmd_ret != 0:
                                os.unlink(new_file)
                                raise XbumpError(new_file, "Can't edit")

                if delete:
                        vinfo('Deleting %s' % old_name)
                        os.unlink(file)
                return eb.get_name()

