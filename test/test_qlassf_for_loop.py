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

from .utils import COMPILATION_ENABLED, compute_and_compare_results

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


class TestForLoop(unittest.TestCase):
    def test_for_1it(self):
        f = "def test(a: Qint2) -> Qint2:\n\tfor x in range(1):\n\t\ta += 1\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_for_3it(self):
        f = "def test(a: Qint2) -> Qint2:\n\tfor i in range(3):\n\t\ta += i\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_for_nit_bool(self):
        f = "def test(a: bool) -> bool:\n\tfor i in range(4):\n\t\ta = not a\n\treturn a"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    # def test_for_cond(self):
    #     f = "def test(a: Qint2, b: bool) -> Qint2:\n\tfor i in range(3):\n\t\ta += (i if b else 1)\n\treturn a"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED)
    #     print(qf.expressions)
    #     compute_and_compare_results(self, qf)
