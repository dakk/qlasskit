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

from sympy import And, Not, Symbol

from qlasskit import Qint2, Qint4, Qlist, qlassf
from qlasskit.algorithms import (
    ConstantOracleException,
    QAlgorithm,
    format_outcome,
    interpret_as_qtype,
    oraclize,
)


class TestAlgo_format_outcome(unittest.TestCase):
    def test_format_outcome_str(self):
        out = "1011"
        self.assertEqual(format_outcome(out), [True, False, True, True])

    def test_format_outcome_str_with_out_len(self):
        out = "1011"
        self.assertEqual(format_outcome(out, 5), [True, False, True, True, False])

    def test_format_outcome_int(self):
        out = 15
        self.assertEqual(format_outcome(out), [True, True, True, True])

    def test_format_outcome_int_with_out_len(self):
        out = 15
        self.assertEqual(format_outcome(out, 5), [True, True, True, True, False])

    def test_format_outcome_bool(self):
        out = [True, True]
        self.assertEqual(format_outcome(out), [True, True])

    def test_format_outcome_bool_with_out_len(self):
        out = [True, True]
        self.assertEqual(format_outcome(out, 3), [True, True, False])


class TestAlgo_interpret_as_type(unittest.TestCase):
    def test_interpret_bool(self):
        _out = interpret_as_qtype([False, True], bool, 1)
        self.assertEqual(_out, True)

    def test_interpret_qint2(self):
        _out = interpret_as_qtype([False, True], Qint2, 2)
        self.assertEqual(_out, 1)

    def test_interpret_qint4(self):
        _out = interpret_as_qtype([True, True, True, False], Qint4, 4)
        self.assertEqual(_out, 14)

    def test_interpret_qlist_bool_3(self):
        _out = list(interpret_as_qtype([True, True, False], Qlist[bool, 3], 3))
        self.assertEqual(_out, [False, True, True])

    def test_interpret_tuple_bool(self):
        _out = interpret_as_qtype([True, True, False], Tuple[bool, bool, bool], 3)
        self.assertEqual(_out, (False, True, True))


class QT(QAlgorithm):
    def __init__(self, tt, ll):
        self.tt = tt
        self.ll = ll

    def interpret_outcome(self, oc):
        return interpret_as_qtype(oc, self.tt, self.ll)


class TestAlgo_interpret_counts(unittest.TestCase):
    def test_interpret_counts(self):
        q = QT(bool, 1)
        c = q.interpet_counts({"010": 3, "110": 2, "111": 1})
        self.assertEqual(c, {False: 5, True: 1})

    def test_interpret_counts2(self):
        q = QT(Tuple[bool, bool], 2)
        c = q.interpet_counts({"010": 3, "110": 2, "111": 1})
        self.assertEqual(c, {(False, True): 5, (True, True): 1})


class TestAlgo_oraclize(unittest.TestCase):
    def test_constant_oracle(self):
        q = qlassf("def test(a: bool) -> bool: return True")
        self.assertRaises(ConstantOracleException, lambda x: oraclize(q, True), True)

    def test_oracle_identity(self):
        q = qlassf("def test(a: bool) -> bool: return a")
        orac = oraclize(q, True)
        self.assertEqual(orac.name, "oracle")
        self.assertEqual(orac.expressions, [(Symbol("_ret"), Symbol("v"))])

    def test_oracle_tuple(self):
        q = qlassf("def test(a: Tuple[bool, bool]) -> bool: return a[0] and a[1]")
        orac = oraclize(q, True)
        self.assertEqual(
            orac.expressions, [(Symbol("_ret"), And(Symbol("v.0"), Symbol("v.1")))]
        )

    def test_oracle_qtype(self):
        q = qlassf("def test(a: Qint2) -> Qint2: return a")
        orac = oraclize(q, 1)
        self.assertEqual(
            orac.expressions, [(Symbol("_ret"), And(Symbol("v.0"), Not(Symbol("v.1"))))]
        )
