# -*- coding: utf-8 -*-
# KivyUnitTest
# Version: 0.1.0
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
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

import os
import sys
import subprocess
import os.path as op
from time import time
from os.path import isfile
from os import listdir as ls


class Test(object):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self._path = op.dirname(op.abspath(__file__))
        try:
            if sys.argv[1] == '--folder':
                self.path = sys.argv[2]
                if self.path.startswith('\'') or self.path.startswith('"'):
                    self.path = self.path[1:]
                if self.path.endswith('\'') or self.path.endswith('"'):
                    self.path = self.path[:-1]
                self.path = self.path.strip('.py')

                self.modules = []
                m = [f for f in ls(self.path) if isfile(op.join(self.path, f))]
                for mod in m:
                    if (mod.startswith('test_') and mod.endswith('.py')):
                        self.modules.append(mod.strip('.py'))
            else:
                self.path = self._path
                self.modules = ['test_text', ]
        except IndexError:
            self.path = self._path
            self.modules = ['test_text', ]
        self.outputs = []

    def run(self):
        self.startTime = time()
        for mod in self.modules:
            args = ['python', '-c',
                    ('import sys; import os.path as op; import unittest;'
                     'sys.path.append(%s); loader = unittest.TestLoader();'
                     'suite = loader.loadTestsFromName("%s");'
                     'runner = unittest.TextTestRunner(verbosity=2);'
                     'result = runner.run(suite);' % (repr(self.path), mod))]
            call = [subprocess.check_output(args, stderr=subprocess.STDOUT)]
            self.outputs.append(call)

        # remove separators
        cleaned = []
        for output in self.outputs:
            _temp = []
            for out in output:
                _temp.append(out.split(os.linesep))
            cleaned.append(_temp)
        self.outputs = cleaned[:]

        # get errors' log
        errors = []
        for i, output in enumerate(self.outputs):
            for j, lines in enumerate(output):
                for line in lines:
                    if line.startswith('Traceback'):
                        module = self.modules[i]
                        errors.append([i, j, module])

        for error in errors:
            print('='*70)
            print('|', error[2], ' '*(61-len(error[2])), 'LOG |')
            print('='*70)
            for line in self.outputs[error[0]][error[1]]:
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
        else:
            print('SUCCESS!')

if __name__ == '__main__':
    Test().run()
