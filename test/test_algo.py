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
from sympy import And, Not, Symbol

from qlasskit import Qint2, Qint4, Qlist, qlassf
from qlasskit.algorithms import ConstantOracleException, QAlgorithm, oraclize
from qlasskit.types import format_outcome, interpret_as_qtype

from .utils import ENABLED_COMPILERS


class QT(QAlgorithm):
    def __init__(self, tt, ll):
        self.tt = tt
        self.ll = ll

    def decode_output(self, oc):
        return interpret_as_qtype(oc, self.tt, self.ll)


class TestAlgo_interpret_counts(unittest.TestCase):
    def test_interpret_counts(self):
        q = QT(bool, 1)
        c = q.decode_counts({"010": 3, "110": 2, "111": 1})
        self.assertEqual(c, {False: 5, True: 1})

    def test_interpret_counts2(self):
        q = QT(Tuple[bool, bool], 2)
        c = q.decode_counts({"010": 3, "110": 2, "111": 1})
        self.assertEqual(c, {(False, True): 5, (True, True): 1})


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestAlgo_oraclize(unittest.TestCase):
    def test_constant_oracle(self):
        q = qlassf("def test(a: bool) -> bool: return True", compiler=self.compiler)
        self.assertRaises(ConstantOracleException, lambda x: oraclize(q, True), True)

    def test_oracle_identity(self):
        q = qlassf("def test(a: bool) -> bool: return a", compiler=self.compiler)
        orac = oraclize(q, True)
        orac.compile(compiler=self.compiler)
        self.assertEqual(orac.name, "oracle")
        self.assertEqual(orac.expressions, [(Symbol("_ret"), Symbol("v"))])

    def test_oracle_tuple(self):
        q = qlassf(
            "def test(a: Tuple[bool, bool]) -> bool: return a[0] and a[1]",
            compiler=self.compiler,
        )
        orac = oraclize(q, True)
        orac.compile(compiler=self.compiler)
        self.assertEqual(
            orac.expressions, [(Symbol("_ret"), And(Symbol("v.0"), Symbol("v.1")))]
        )

    def test_oracle_qtype(self):
        q = qlassf("def test(a: Qint2) -> Qint2: return a", compiler=self.compiler)
        orac = oraclize(q, 1)
        orac.compile(compiler=self.compiler)
        self.assertEqual(
            orac.expressions, [(Symbol("_ret"), And(Symbol("v.0"), Not(Symbol("v.1"))))]
        )
