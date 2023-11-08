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

from qlasskit import QlassF, exceptions, qlassf

from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfIfThenElse(unittest.TestCase):
    def test_if_else(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\tif a:\n"
            + "\t\td = not a\n"
            + "\telse:\n"
            + "\t\td = True\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_if_unbound(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\tif a:\n"
            + "\t\td = not a\n"
            + "\treturn d"
        )
        self.assertRaises(
            exceptions.UnboundException,
            lambda f: qlassf(f, to_compile=COMPILATION_ENABLED),
            (f),
        )

    def test_if(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\tif a:\n"
            + "\t\td = not a\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_if_for(self):
        f = (
            "def test(a: bool, b: bool) -> bool:\n"
            + "\td = False\n"
            + "\ti = 0\n"
            + "\tif a:\n"
            + "\t\tfor i in range(3):\n"
            + "\t\t\td = not d\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)

    def test_if_for2(self):
        f = (
            "def test(a: bool, b: bool) -> Qint2:\n"
            + "\td = 0\n"
            + "\tfor i in range(3):\n"
            + "\t\tif a:\n"
            + "\t\t\td += 1\n"
            + "\treturn d"
        )
        qf = qlassf(f, compiler=self.compiler, to_compile=COMPILATION_ENABLED)
        compute_and_compare_results(self, qf)
