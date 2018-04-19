#!/usr/bin/python
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

from __future__ import print_function

import glob
import os
import subprocess
import sys
from unittest import TextTestRunner, TestLoader

from setuptools import setup, Command


class TestCoverage(object):
    def __init__(self):
        try:
            import coverage
            self.cov = coverage
        except ImportError:
            print("Can't find the coverage module")
            self.cov = None
            return

    def start(self):
        if not self.cov:
            return
        self.cov.erase()
        self.cov.start()

    def stop(self):
        if not self.cov:
            return
        self.cov.stop()

    def report(self, packages):
        if not self.cov:
            return
        print('\nCoverage report:')
        report_list = []
        for package in packages:
            for root, _, files in os.walk(package):
                for file_ in files:
                    if file_.endswith('.py'):
                        report_list.append('%s/%s' % (root, file_))
        self.cov.report(report_list)


class TestCommand(Command):
    user_options = [('coverage', 'c', 'Enable coverage output')]
    boolean_options = ['coverage']

    _dir = None
    coverage = None

    def initialize_options(self):
        self._dir = os.getcwd()
        self.coverage = False

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        if self.coverage:
            cov = TestCoverage()
            cov.start()

        testfiles = []
        for t in glob.glob(os.path.join(self._dir, 'tests', 'test_xbump_*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(['tests', os.path.splitext(os.path.basename(t))[0]]))

        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity=1)
        ts = t.run(tests)

        if self.coverage:
            cov.stop()
            cov.report(self.distribution.packages)

        if not ts.wasSuccessful():
            sys.exit(1)


class FmtCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def _find_py():
        r""" find -name \*.py """
        for root, _, files in os.walk('.'):
            for fname in files:
                if os.path.splitext(fname)[1] == '.py':
                    yield os.path.join(root, fname)

    def run(self):
        print('* running unify')
        subprocess.check_call(['unify', '-i', '-r', '.'])
        print('* running yapf')
        subprocess.check_call(['yapf', '-i'] + list(self._find_py()))


setup(
    name='xintegtools',
    version='3.1.1',
    description='Xintegtools for genbox',
    author='Wyplay',
    author_email='noreply@wyplay.com',
    url='http://www.wyplay.com',
    packages=[
        'xintegtools',
        'xintegtools.xbump',
        'xintegtools.xreport',
    ],
    scripts=[
        'scripts/xbump',
        'scripts/xreport',
    ],
    long_description="""xintegtools for genbox like xbump, xreport""",
    cmdclass={
        'test': TestCommand,
        'fmt': FmtCommand,
    }
)
