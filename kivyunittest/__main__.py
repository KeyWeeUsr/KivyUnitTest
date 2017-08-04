# -*- coding: utf-8 -*-
# KivyUnitTest
# Copyright (C) 2016 - 2017, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
# License: The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# More info in LICENSE.txt
#
# The above copyright notice, warning and additional info together with
# LICENSE.txt file shall be included in all copies or substantial portions
# of the Software.

# Each test _needs_ a fresh python, otherwise only a single test will run

from __future__ import print_function
from argparse import ArgumentParser

import os
import sys
import os.path as op
from time import time
import subprocess as subp
from os.path import isfile, join, dirname, abspath
from os import listdir as ls

__version__ = '0.1.6'


class Parser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(
            prog='KivyUnitTest',
            epilog=(
                'WARNING: if there are files with the same name, '
                'only the file in the first folder will be run!'
            )
        )

        self.add_argument(
            '-V', '--version',
            action='version',
            version='%(prog)s %(ver)s' % {
                'prog': self.prog, 'ver': __version__
            }
        )
        self.add_argument(
            '-v', '--verbose', action='count', default=0,
            help=(
                'increase verbosity of the Kivy output, '
                'can stack up to 2 times to achieve different log output'
            )
        )
        self.add_argument(
            '--demo', action='store_true',
            help=(
                'run demo for the %(prog)s'
            )
        )
        self.add_argument(
            '-d', '--folder',
            type=str, nargs='+', metavar='DIR', default=[],
            help=(
                'list of folders with test files, '
                'defaults to: %(default)s'
            ),
        )
        self.add_argument(
            '-p', '--pythonpath',
            type=str, nargs='+', metavar='DIR',
            default=[
                dirname(abspath(__file__))
            ],
            help=(
                'list of non-standard paths to import modules from, '
                'defaults to: %(default)s'
            )
        )


class Test(object):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)

        self.path = []
        self.modules = []
        self.outputs = []
        self.log_level = ['info', 'debug', 'trace']

        # override --folder & --pythonpath args if running demo
        if parse.demo:
            parse.folder = [
                join(dirname(abspath(__file__)), 'examples')
            ]
            parse.pythonpath = [
                dirname(abspath(__file__))
            ]

        self.path.extend(parse.folder)

        mods = [
            f for path in self.path for f in ls(path) if isfile(join(path, f))
        ]
        for mod in mods:
            if (mod.startswith('test_') and mod.endswith('.py')):
                self.modules.append(mod.strip('.py'))

        if parse.pythonpath:
            # optional arg path first
            self.path = parse.pythonpath + self.path

    def run(self):
        self.startTime = time()

        for mod in self.modules:
            args = [
                'python', '-c', (
                    'import sys;'
                    'import unittest;'
                    'from kivy.config import Config;'
                    'sys.path = %(path)s + sys.path;'
                    'Config.set("kivy", "log_level", "%(level)s");'
                    'loader = unittest.TestLoader();'
                    'suite = loader.loadTestsFromName("%(module)s");'
                    'runner = unittest.TextTestRunner(verbosity=0);'
                    'result = runner.run(suite);' % {
                        'path': repr(self.path),
                        'module': mod,
                        'level': self.log_level[parse.verbose]
                    }
                )
            ]

            try:
                call = [subp.check_output(args, stderr=subp.STDOUT)]
            except subp.CalledProcessError as exc:
                call = [exc.output]
            self.outputs.append(call)

        # remove separators
        cleaned = []
        for output in self.outputs:
            _temp = []
            for out in output:
                try:
                    _temp.append(out.split(os.linesep))
                except TypeError:
                    _temp.append(out.split(os.linesep.encode('utf-8')))
            cleaned.append(_temp)
        self.outputs = cleaned[:]

        # get errors' log
        errors = []
        for i, output in enumerate(self.outputs):
            for j, lines in enumerate(output):
                for line in lines:
                    try:
                        if line.startswith('Traceback'):
                            module = self.modules[i]
                            errors.append([i, j, module])
                    except TypeError:
                        # in py3 it's ' Traceback' (with whitespace) O_o
                        if line.startswith(b' Traceback'):
                            module = self.modules[i]
                            errors.append([i, j, module])

        for error in errors:
            print('='*70)
            print('|', error[2], ' '*(61-len(error[2])), 'LOG |')
            print('='*70)
            for line in self.outputs[error[0]][error[1]]:
                if sys.version_info[0] == 3:
                    print(line.decode('utf-8'))
                else:
                    print(line)

        delta = round(time() - self.startTime, 3)
        len_mod = len(self.modules)
        if len_mod == 1:
            print('Ran %s test in %ss' % (len_mod, delta))
        else:
            print('Ran %s tests in %ss' % (len_mod, delta))
        if errors:
            len_err = len(errors)
            if len_err == 1:
                msg = '%s FAILED TEST!' % len_err
            else:
                msg = '%s FAILED TESTS!' % len_err
            print(msg)
            exit(1)
        else:
            print('SUCCESS!')

if __name__ == '__main__':
    parse = Parser().parse_args()
    Test().run()
