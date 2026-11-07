# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest

from parameterized import parameterized_class

from qlasskit import qlassf

from ..utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


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

    def test_inner_function1(self):
        f = """def test(a: bool) -> bool:
    def test2(b:bool) -> bool:
        return not b
    return test2(a)"""
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_inner_function2(self):
        f = """def test(a: bool, z: bool) -> bool:
    def test2(b:bool) -> bool:
        return not b
    def test3(b:bool, c:bool) -> bool:
        return b and c
    return test3(test2(a), z)"""
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)

    def test_inner_function3(self):
        f = """def test(a: bool) -> bool:
    def test2(b:bool) -> bool:
        def test3(b:bool) -> bool:
            return not b
        return not test3(b)
    return test2(a)"""
        qf = qlassf(f, to_compile=COMPILATION_ENABLED, compiler=self.compiler)
        compute_and_compare_results(self, qf)
