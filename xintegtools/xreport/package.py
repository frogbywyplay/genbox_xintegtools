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

import os, errno

from pkgsplit import pkgsplit
from hashlib import md5
from report_utils import readfile

def md5sum(fname):
        '''Returns an md5 hash for a file with read() method.'''
        f = file(fname, 'rb')
        m = md5()
        while True:
                d = f.read(8096)
                if not d:
                        break
                m.update(d)
        f.close()
        return m.hexdigest()


class XPackageFile(object):
        _status = [
                "ENOENT",
                "ECHKSUM",
                "EMTIME"
        ]
        def __init__(self, name, type):
                self.name = name.decode('utf-8')
                self.type = type
                self.checked = False
                self.md5sum = None
                self.mtime = None
                self.status = {}

        def set_mtime(self, mtime):
                self.mtime = int(mtime)

        def set_md5sum(self, md5):
                self.md5sum = md5

        def set_dest(self, dest):
                self.dest = dest

        def _check_obj(self, root):
                try:
                        stat = os.stat(root + self.name)
                except OSError, e:
                        if e.errno == errno.ENOENT:
                                self.status["ENOENT"] = True
                                return False 
                        raise 

                md5 = md5sum(root + self.name)
                if md5 != self.md5sum:
                        self.status["ECHKSUM"] = md5
                        return False

                if stat.st_mtime != self.mtime:
                        self.status["EMTIME"] = stat.st_mtime
                        return False

                return True
                
        def check(self, root):
                self.checked = True
                if self.type == "obj":
                        return self._check_obj(root)
                return True

class XPackage(object):
        _contents_split_counts = {
                "dev": 2,
                "dir": 2,
                "fif": 2,
                "obj": 4,
                "sym": 5
        }
        def __init__(self, vdbdir, cat=None, name=None):
                self.cat = cat
                self.name = name
                self.vdbdir = vdbdir
                self.pkgfiles = None
                self.uses = None
                self.licenses = None
                self.license_choosen = None
                self.public = False
                self.scm = None
                self.res = 0

                pkg_split = pkgsplit(name)
                self.short_name = pkg_split[0]
                if len(pkg_split) >= 3 and pkg_split[2] == "r0":
                        self.version = pkg_split[1]
                else:
                        self.version = "-".join(pkg_split[1:])

                self.load_pkg(vdbdir)

        def _load_contents(self, vdbdir):
                if self.pkgfiles:
                        del self.pkgfiles
                self.pkgfiles = []
                null_byte = '\0'

                lines = readfile(vdbdir + "/CONTENTS")
                for line in lines:
			if null_byte in line:
				# Null bytes are a common indication of corruption.
                                # FIXME raise something
				continue
			mydat = line.split()
			# we do this so we can remove from non-root filesystems
			# (use the ROOT var to allow maintenance on other partitions)
			try:
#				mydat[1] = normalize_path(os.path.join(
#					self.myroot, mydat[1].lstrip(os.path.sep)))
				if mydat[0]=="obj":
					#format: type, mtime, md5sum
                                        pkg = XPackageFile(" ".join(mydat[1:-2]), mydat[0])
                                        pkg.set_mtime(mydat[-1])
                                        pkg.set_md5sum(mydat[-2])
                                        self.pkgfiles.append(pkg)
				elif mydat[0]=="dir":
					#format: type
                                        self.pkgfiles.append(XPackageFile(" ".join(mydat[1:]), mydat[0]))
				elif mydat[0]=="sym":
					#format: type, mtime, dest
					x=len(mydat)-1
					if (x >= 13) and (mydat[-1][-1]==')'): # Old/Broken symlink entry
						mydat = mydat[:-10]+[mydat[-10:][stat.ST_MTIME][:-1]]
						x=len(mydat)-1
					splitter=-1
					while(x>=0):
						if mydat[x]=="->":
							splitter=x
							break
						x=x-1
					if splitter==-1:
						return None
                                        pkg = XPackageFile(" ".join(mydat[1:splitter]), mydat[0])
                                        pkg.set_mtime(mydat[-1])
                                        pkg.set_dest(" ".join(mydat[(splitter+1):-1]))
                                        self.pkgfiles.append(pkg)
				elif mydat[0]=="dev":
					#format: type
					self.pkgfiles.append(XPackageFile(" ".join(mydat[1:]), mydat[0]))
				elif mydat[0]=="fif":
					#format: type
					self.pkgfiles.append(XPackageFile(" ".join(mydat[1:]), mydat[0]))
				else:
					return None
			except (KeyError,IndexError):
				print "package: CONTENTS line",pos,"corrupt!"

        def _load_uses(self, vdbdir):
                if self.uses:
                        del self.uses

                try:
                        iuse = readfile(vdbdir + "/IUSE", True).split()
                except IOError:
                        # No use flags for this package
                        return

                self.uses = {}

                use = readfile(vdbdir + "/USE", True).split()
                for flag in iuse:
                        if flag in use:
                                self.uses[flag] = True
                        else:
                                self.uses[flag] = False

        def _load_license(self, vdbdir):
                try:
                        licenses = readfile(vdbdir + "/LICENSE", True)
                except IOError:
                        return
                self.licenses = licenses.split()

                try:
                        choosen = readfile(vdbdir + "/LICENSE_CHOOSEN", True).strip()
                        for l in self.licenses:
                                if l == choosen:
                                        self.license_choosen = l
                                        break
                except IOError:
                        if len(self.licenses) > 1:
                                self.license_choosen = licenses[0]

                if os.path.exists(vdbdir + "/PUBLIC"):
                        self.public = True

        def _load_mercurial(self, vdbdir):
                scm = {'type': 'mercurial'}
                try:
                        for kk, vv in [('uri', 'EHG_REPO_URI'),
                                       ('branch', 'EHG_BRANCH'),
                                       ('revision', 'EHG_REVISION')]:
                                # split is to avoid extra '\n'
                                scm[kk] = readfile('%s/%s' % (vdbdir, vv), True).split()[0]
                except IOError:
                        # don't know what to do
                        pass
                else:
                        self.scm = scm
                return
        
        def _load_git(self, vdbdir):
                scm = {'type': 'git'}
                for kk, vv in [('uri', 'EGIT_REPO_URI'),
                               ('group', 'EGIT_GROUP'),
                               ('branch', 'EGIT_BRANCH'),
                               ('revision', 'EGIT_REV')]:
                                # split is to avoid extra '\n'
                        try:
                                scm[kk] = readfile('%s/%s' % (vdbdir, vv), True).split()[0]
                        except IOError:
                                pass #skip missing files
                self.scm = scm
                return
        
        def _load_scm(self, vdbdir):
                try:
                        inherited = readfile('%s/INHERITED' % vdbdir, True).split()
                        if 'mercurial' in inherited:
                                self._load_mercurial(vdbdir)
                        elif 'git' in inherited:
                                self._load_git(vdbdir)
                except IOError:
                        self.scm = None
        
        def load_pkg(self, vdbdir):
                self._load_contents(vdbdir)
                self._load_uses(vdbdir)
                self._load_license(vdbdir)
                self._load_scm(vdbdir)

