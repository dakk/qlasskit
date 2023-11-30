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

from .utils import (
    COMPILATION_ENABLED,
    ENABLED_COMPILERS,
    compute_and_compare_results,
    inject_parameterized_compilers,
)

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfZXSimp(unittest.TestCase):
    def test_int_const_compare_eq(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a == 2"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        qf.circuit().zx_simplify()
        compute_and_compare_results(self, qf)

    # def test_const_int_compare_gt(self):
    #     f = f"def test(a: Qint2) -> bool:\n\treturn a > 2"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     qf.circuit().zx_simplify()
    #     compute_and_compare_results(self, qf)

    # def test_ite_return_qint(self):
    #     f = "def test(a: bool, b: Qint2, c: Qint2) -> Qint2:\n\treturn b if a else c"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    # def test_composed_comparators(self):
    #     f = "def f_comp(n: Qint4) -> bool: return n > 3 or n == 7"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    # def test_add(self):
    #     f = "def test(a: Qint2, b: Qint2) -> Qint2: return a + b"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

    # def test_add_const(self):
    #     f = "def test(a: Qint2) -> Qint2: return a + 1"
    #     qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
    #     compute_and_compare_results(self, qf)

