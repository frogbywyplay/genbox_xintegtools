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

import sys, os

try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

from output import XReportOutput, XCompareOutput


class XReportXMLOutput(XReportOutput):
    def __init__(self, errors_only=False, contents=False):
        self.root = None
        self.tree = None
        self.packages = None
        XReportOutput.__init__(self, errors_only, contents)

    def _header(self, output_file):
        if self.root is not None:
            del self.root
        if self.tree is not None:
            del self.tree
        self.root = etree.Element('target')
        self.packages = etree.Element('packages')
        self.root.append(self.packages)
        self.tree = etree.ElementTree(self.root)

    def _footer(self, output_file):
        self.packages = None

    def _package(self, pkg, output_file):
        total_files = len(pkg.pkgfiles)
        if self.errors_only and pkg.res == total_files:
            return

        xml_pkg = etree.Element('package', name=pkg.short_name, version=pkg.version, category=pkg.cat)
        self.packages.append(xml_pkg)

        if pkg.licenses:
            for l in pkg.licenses:
                if pkg.license_choosen == l:
                    xml_license = etree.Element('license', name=l, choosen='True')
                else:
                    xml_license = etree.Element('license', name=l)
                xml_pkg.append(xml_license)

        if pkg.public:
            xml_public = etree.Element('public')
            xml_pkg.append(xml_public)

        if pkg.uses != None:
            xml_uses = etree.Element('use_flags')
            xml_pkg.append(xml_uses)

            for use, val in sorted(pkg.uses.items()):
                if val:
                    use_elt = etree.Element('use', name=use, val='1')
                else:
                    use_elt = etree.Element('use', name=use)
                xml_uses.append(use_elt)

        xml_contents = etree.Element('contents')
        xml_pkg.append(xml_contents)

        if self.errors_only and (pkg.res == total_files):
            return
        for file in pkg.pkgfiles:
            if self.errors_only and not (file.status and len(file.status)):
                continue
            # Omit directories (not really useful)
            if file.type == 'dir':
                continue
            xml_file = etree.Element('file', name=file.name, type=file.type)
            xml_contents.append(xml_file)
            if file.md5sum is not None:
                md5 = etree.Element('md5')
                md5.text = file.md5sum
                xml_file.append(md5)
            if file.mtime is not None:
                mtime = etree.Element('mtime')
                mtime.text = str(file.mtime)
                xml_file.append(mtime)

            if file.status and len(file.status):
                xml_rep = etree.Element('report')
                xml_file.append(xml_rep)

                for error in file.status:
                    if error == 'EMTIME':
                        xml_rep.append(etree.Element('EMTIME', mtime=str(file.status['EMTIME'])))
                    elif error == 'ECHKSUM':
                        xml_rep.append(etree.Element('ECHKSUM', md5=file.status['ECHKSUM']))
                    elif error == 'ENOENT':
                        xml_rep.append(etree.Element('ENOENT'))
                    else:
                        xml_rep.append(etree.Element('EUNKNOWN'))

        if pkg.scm:
            xml_scm = etree.Element('scm', type=pkg.scm['type'])
            xml_pkg.append(xml_scm)
            for ii in ['uri', 'group', 'branch', 'revision']:
                try:
                    scm_elt = etree.Element(ii)
                    scm_elt.text = pkg.scm[ii]
                    xml_scm.append(scm_elt)
                except KeyError, e:
                    pass

    def _collisions(self, collisions, output_file):
        if not collisions or len(collisions) == 0:
            return
        xml_col = etree.Element('collisions')
        self.root.append(xml_col)
        for file, pkgs in sorted(collisions.items()):
            xml_file = etree.Element('file', name=file)
            xml_col.append(xml_file)
            for pkg in pkgs:
                xml_file.append(etree.Element('package', name=pkg))

    def _orphans(self, orphans, output_file):
        if not orphans or len(orphans) == 0:
            return
        xml_orp = etree.Element('orphans')
        self.root.append(xml_orp)
        for orphan in sorted(orphans.keys()):
            xml_orp.append(etree.Element('file', name=orphan))

    def process(self, report, output_file):
        XReportOutput.process(self, report, output_file)
        indent(self.root)
        self.tree.write(output_file, 'utf-8')


class XCompareXMLOutput(XCompareOutput):
    def __init__(self):
        self.root = None
        self.tree = None
        XCompareOutput.__init__(self)

    def _header(self, output_file):
        if self.root is not None:
            del self.root
        if self.tree is not None:
            del self.tree
        self.root = etree.Element('target')
        self.packages = etree.Element('packages')
        self.root.append(self.packages)
        self.tree = etree.ElementTree(self.root)

    def _footer(self, output_file):
        self.packages = None

    def _process_version(self, old, new):
        xml_vers = None
        if old:
            xml_vers = etree.Element('version')
            xml_old = etree.Element('old')
            xml_old.text = old
            xml_vers.append(xml_old)
        if new:
            if not xml_vers:
                xml_vers = etree.Element('version')
            xml_new = etree.Element('new')
            xml_new.text = new
            xml_vers.append(xml_new)
        return xml_vers

    def _get_flag(self, use, type, val):
        xml_use = etree.Element('use', name=use)
        if type == 'new':
            xml_use.set('mod', 'new')
            xml_use.set('val', val)
        elif type == 'mod':
            xml_use.set('mod', 'mod')
            xml_use.set('val', val)
        elif type == 'rem':
            xml_use.set('mod', 'rem')
        return xml_use

    def _process_flags(self, flags):
        if not flags:
            return None
        xml_uses = etree.Element('use_flags')
        for use, val in flags.iteritems():
            xml_uses.append(self._get_flag(use, val[0], val[1]))
        return xml_uses

    def process(self, compare, output_file=sys.stdout):
        self._header(output_file)
        for pkg_id, pkg in compare.pkg_diff.iteritems():
            full_name = pkg_id.rsplit(':', 1)
            if pkg is None:
                die('Internal error when parsing comparison results')

            cat, name = full_name[0].split('/')

            xml_pkg = etree.Element('package', name=name, category=cat)
            self.packages.append(xml_pkg)

            child = self._process_version(pkg.get('old'), pkg.get('new'))
            if child:
                xml_pkg.append(child)

            child = self._process_flags(pkg.get('use'))
            if child:
                xml_pkg.append(child)

        self._footer(output_file)
        indent(self.root)
        self.tree.write(output_file, 'utf-8')


def indent(elem, level=0):
    i = '\n' + level * '  '
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + '  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
