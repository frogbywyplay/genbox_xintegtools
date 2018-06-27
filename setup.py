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

import contextlib
import glob
import os
import subprocess
import sys
from unittest import TextTestRunner, TestLoader

from setuptools import setup, Command

try:
    import coverage

    @contextlib.contextmanager
    def cov(packages):
        def report_list_aux():
            for package in packages:
                for root, _, files in os.walk(package):
                    for fname in files:
                        if fname.endswith('.py'):
                            yield os.path.join(root, fname)

        report_list = list(set(report_list_aux()))
        c = coverage.Coverage()
        c.erase()
        c.start()
        yield
        c.stop()
        print('\nCoverage report:')
        c.report(report_list)

except ImportError:
    print("Can't find the coverage module")

    @contextlib.contextmanager
    def cov(_):
        yield


class TestCommand(Command):
    user_options = [('coverage', 'c', 'Enable coverage output')]
    boolean_options = ['coverage']

    coverage = None

    def initialize_options(self):
        self.coverage = False

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''

        testfiles = [
            '.'.join(['tests', os.path.splitext(os.path.basename(t))[0]])
            for t in glob.glob(os.path.join('tests', 'test_xbump_*.py')) if not t.endswith('__init__.py')
        ]

        with cov(self.distribution.packages):
            tests = TestLoader().loadTestsFromNames(testfiles)
            t = TextTestRunner()
            ts = t.run(tests)

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
        'scripts/xreport',
    ],
    entry_points={'console_scripts': ['xbump = xintegtools.xbump.main:main']},
    long_description="""xintegtools for genbox like xbump, xreport""",
    cmdclass={
        'test': TestCommand,
        'fmt': FmtCommand,
    }
)
