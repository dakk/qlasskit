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

from sympy import Symbol

from qlasskit import qlassf

from ..utils import COMPILATION_ENABLED, compute_and_compare_results


class TestQlassfParameters(unittest.TestCase):
    def test_bind_bool(self):
        uqf = qlassf(
            "def test(c: Parameter[bool], a: bool) -> bool: return a and c",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=True)
        self.assertEqual(qf.expressions[0][1], Symbol("a"))
        compute_and_compare_results(self, qf)

        qf = uqf.bind(c=False)
        self.assertEqual(qf.expressions[0][1], False)
        compute_and_compare_results(self, qf)

    def test_bind_qint2(self):
        uqf = qlassf(
            "def test(c: Parameter[Qint2], a: bool) -> Qint2: return c+1 if a else c",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=1)
        compute_and_compare_results(self, qf)

    def test_bind_multiple_qint2(self):
        uqf = qlassf(
            (
                "def test(c: Parameter[Qint2], d: Parameter[Qint2], a: bool) -> Qint2: "
                "return c+d if a else c+1"
            ),
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=1, d=2)
        compute_and_compare_results(self, qf)

    def test_bind_list(self):
        uqf = qlassf(
            "def test(c: Parameter[Qlist[2, bool]]) -> bool: return c[0] and c[1]",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=[True, True])
        compute_and_compare_results(self, qf)

    def test_bind_tuple(self):
        uqf = qlassf(
            "def test(c: Parameter[Tuple[bool, Qint2]]) -> Qint2: return c[1] if c[0] else c[1]+1",
            to_compile=COMPILATION_ENABLED,
        )
        qf = uqf.bind(c=(True, 2))
        compute_and_compare_results(self, qf)
