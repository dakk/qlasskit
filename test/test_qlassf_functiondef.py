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
from typing import Tuple

from parameterized import parameterized_class
from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfFunctionDef(unittest.TestCase):
    def test_pass_another_function(self):
        f = "def neg(b: bool) -> bool:\n\treturn not b"
        g = "def test(a: bool) -> bool:\n\treturn neg(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        qg = qlassf(g, to_compile=COMPILATION_ENABLED, defs=[qf])
        compute_and_compare_results(self, qf)
        compute_and_compare_results(self, qg, test_original_f=False)

    def test_pass_multiarg_function(self):
        f = "def neg(b: bool, c: bool) -> bool:\n\treturn not b and c"
        g = "def test(a: bool, ff: bool) -> bool:\n\treturn neg(a, ff)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        qg = qlassf(g, to_compile=COMPILATION_ENABLED, defs=[qf])
        compute_and_compare_results(self, qf)
        compute_and_compare_results(self, qg, test_original_f=False)

    def test_pass_tuplearg_function(self):
        f = "def neg(b: Tuple[bool, bool]) -> bool:\n\treturn not b[0] and b[1]"
        g = "def test(a: bool, ff: bool) -> bool:\n\treturn neg((a, ff))"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        qg = qlassf(g, to_compile=COMPILATION_ENABLED, defs=[qf])
        compute_and_compare_results(self, qf)
        compute_and_compare_results(self, qg, test_original_f=False)

    def test_pass_multires_function(self):
        f = "def neg(b: bool) -> Tuple[bool, bool]:\n\treturn (not b, b)"
        g = "def test(a: bool) -> bool:\n\tc = neg(a)\n\treturn c[0]"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        qg = qlassf(g, to_compile=COMPILATION_ENABLED, defs=[qf])
        compute_and_compare_results(self, qf)
        compute_and_compare_results(self, qg, test_original_f=False)

    def test_pass_multi_stmt_function(self):
        f = "def neg(b: bool) -> bool:\n\tc=not b\n\td=not c\n\treturn d"
        g = "def test(a: bool) -> bool:\n\treturn neg(a)"
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        qg = qlassf(g, to_compile=COMPILATION_ENABLED, defs=[qf])
        compute_and_compare_results(self, qf)
        compute_and_compare_results(self, qg, test_original_f=False)

    def test_inner_function(self):
        f = """def test(a: bool) -> bool:
    def test2(b:bool) -> bool:
        return not b
    return test2(a)"""
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
