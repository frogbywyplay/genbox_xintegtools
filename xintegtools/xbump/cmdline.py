#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
#

import os, re

from xutils import warn, error, info, is_verbose, die
from bump import XbumpError, Xbump, XbumpWarn, error_fmt

from consts import XBUMP_DEF_NAMING

class XbumpCmdline(Xbump):
        def __init__(self):
                return
        
        def update_all(self, pkg, dir, force=False):
                try:
                        self.pkg_re = re.compile(pkg)
                except re.error, v:
                        die("Invalid expression: " + str(v))
                self.force = force

                if dir is None:
                        dir = os.getcwd()
                def update_func(xb, dirname, fnames):
                        for file in fnames:
                                if file.endswith(".ebuild") and \
                                   xb.pkg_re.search(file):
                                        ebuild = "%s/%s" % (dirname, file)
                                        try:
                                                ebuild = Xbump.update(xb, ebuild, None, xb.force)
                                                info(error_fmt(ebuild, "CREATED", None))
                                        except XbumpError, e:
                                                error(str(e))
                                                if is_verbose() and e.get_log():
                                                        print e.get_log()
                                        except XbumpWarn, e:
                                                warn(str(e))
                                                if is_verbose() and e.get_log():
                                                        print e.get_log()

                os.path.walk(dir, update_func, self)
                del self.pkg_re
                del self.force

        def update(self, file, version=None, force=False, name=XBUMP_DEF_NAMING):
                try:
                        ebuild = Xbump.update(self, file, version, force, name)
                        info(error_fmt(ebuild, "CREATED", None))
                except XbumpError, e:
                        error(str(e))
                        if is_verbose() and e.get_log():
                                print e.get_log()
                except XbumpWarn, e:
                        warn(str(e))
                        if is_verbose() and e.get_log():
                                print e.get_log()

        def bump(self, file, delete=False, edit=False):
                try:
                        ebuild = Xbump.bump(self, file, delete, edit)
                        info(error_fmt(ebuild, "CREATED", None))
                except XbumpError, e:
                        error(str(e))
                        if is_verbose() and e.get_log():
                                print e.get_log()
                except XbumpWarn, e:
                        warn(str(e))
                        if is_verbose() and e.get_log():
                                print e.get_log()

