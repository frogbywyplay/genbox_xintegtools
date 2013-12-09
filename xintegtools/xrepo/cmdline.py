#
# Copyright (C) 2006-2013 Wyplay, All Rights Reserved.
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
