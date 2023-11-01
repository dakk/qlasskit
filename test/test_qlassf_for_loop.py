# Copyright 2023 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from parameterized import parameterized_class
from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, Xor, false, simplify_logic, true

from qlasskit import Qint2, Qint4, Qint8, QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestForLoop(unittest.TestCase):
    def test_for_1it(self):
        f = "def test(a: Qint2) -> Qint2:\n\tfor x in range(1):\n\t\ta += 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_4it(self):
        f = "def test(a: Qint2) -> Qint2:\n\tfor x in range(4):\n\t\ta += 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_3it(self):
        f = "def test(a: Qint2) -> Qint2:\n\tfor i in range(3):\n\t\ta += i\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_nit_bool(self):
        f = "def test(a: bool) -> bool:\n\tfor i in range(4):\n\t\ta = not a\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_nit_bool_many(self):
        f = "def test(a: bool) -> bool:\n\tfor i in range(15):\n\t\ta = not a\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    # def test_for_nit_tbool_many(self):
    #     f = "def test(a: Tuple[bool,bool]) -> Tuple[bool,bool]:\n\tfor i in range(32):\n\t\ta[0] = not a[0]\n\t\ta[1] = not a[1]\n\treturn a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    def test_for_cond(self):
        f = "def test(a: Qint2, b: bool) -> Qint2:\n\tfor i in range(2):\n\t\ta += (i if b else 1)\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_sum(self):
        f = "def hash(k: Qint4) -> bool:\n\tz = 1\n\tfor i in range(3):\n\t\tz += i\n\treturn z == 3"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_for_sum2(self):
        f = "def hash(k: Qlist[bool, 4]) -> bool:\n\th = True\n\tfor i in range(len(k)):\n\t\th = h and k[i]\n\treturn h"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
