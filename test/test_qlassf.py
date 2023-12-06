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

from qlasskit import Qint, Qint2, Qint4, Qint12, QlassF, exceptions, qlassf
from qlasskit.boolopt.bool_optimizer import defaultOptimizerDebug

from . import utils
from .utils import COMPILATION_ENABLED, ENABLED_COMPILERS, compute_and_compare_results


class TestQlassfDecorator(unittest.TestCase):
    def test_decorator(self):
        c = qlassf(utils.test_not, to_compile=False)
        self.assertTrue(isinstance(c, QlassF))


class TestQlassfOptimizerSelection(unittest.TestCase):
    def test_debug_optimizer(self):
        qf = qlassf(
            "def t(a: bool) -> bool: return a",
            to_compile=COMPILATION_ENABLED,
            bool_optimizer=defaultOptimizerDebug,
        )
        compute_and_compare_results(self, qf)


@parameterized_class(("compiler"), ENABLED_COMPILERS)
class TestQlassfCustomTypes(unittest.TestCase):
    def test_custom_qint5(self):
        qf = qlassf(
            utils.test_qint5,
            types=[utils.Qint5],
            to_compile=COMPILATION_ENABLED,
            compiler=self.compiler,
        )
        compute_and_compare_results(self, qf)

    def test_custom_qint5_notfound(self):
        self.assertRaises(
            exceptions.UnknownTypeException,
            lambda f: qlassf(
                f, types=[], to_compile=COMPILATION_ENABLED, compiler=self.compiler
            ),
            utils.test_qint5,
        )


class TestQlassfEncodeInputDecodeOutput(unittest.TestCase):
    def test_encode_decode_bool(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(qf.encode_input(True), "1")
        self.assertEqual(qf.decode_output("1"), True)

        self.assertEqual(qf.encode_input(False), "0")
        self.assertEqual(qf.decode_output("0"), False)

    def test_encode_decode_qint(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(qf.encode_input(Qint2(2)), "01"[::-1])
        self.assertEqual(qf.decode_output("01"[::-1]), Qint2(2))

        self.assertEqual(qf.encode_input(Qint2(0)), "00")
        self.assertEqual(qf.decode_output("00"), Qint2(0))

    def test_encode_decode_tuple(self):
        f = "def test(a: Tuple[Qint2, bool]) -> Tuple[Qint2, bool]:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(qf.encode_input((Qint2(2), False)), "010")
        self.assertEqual(qf.decode_output("010"), (Qint2(2), False))

        self.assertEqual(qf.encode_input((Qint2(0), True)), "001"[::-1])
        self.assertEqual(qf.decode_output("001"[::-1]), (Qint2(0), True))

    def test_encode_decode_tuple2(self):
        f = "def test(a: Tuple[Qint2, Qint4]) -> Tuple[Qint2, Qint4]:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(qf.encode_input((Qint2(2), Qint4(3))), "011100"[::-1])
        self.assertEqual(qf.decode_output("011100"[::-1]), (Qint2(2), Qint4(3)))

        self.assertEqual(qf.encode_input((Qint2(0), Qint4(2))), "000100"[::-1])
        self.assertEqual(qf.decode_output("000100"[::-1]), (Qint2(0), Qint4(2)))


class TestQlassfTruthTable(unittest.TestCase):
    def test_not_truth(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [[False, True], [True, False]],
        )

    def test_and_truth(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a and b"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [
                [False, False, False],
                [False, True, False],
                [True, False, False],
                [True, True, True],
            ],
        )

    def test_or_truth(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a or b"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [
                [False, False, False],
                [False, True, True],
                [True, False, True],
                [True, True, True],
            ],
        )

    def test_or_not_truth(self):
        f = "def test(a: bool, b: bool) -> bool:\n\treturn a or b"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        self.assertEqual(
            tt,
            [
                [False, False, False],
                [False, True, True],
                [True, False, True],
                [True, True, True],
            ],
        )

    def test_big_truth(self):
        f = "def test(a: Qint4) -> Qint4:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        tt = qf.truth_table()
        tth = qf.truth_table_header()

        self.assertEqual(
            tth, ["a.0", "a.1", "a.2", "a.3", "_ret.0", "_ret.1", "_ret.2", "_ret.3"]
        )
        self.assertEqual(
            tt,
            [
                [False, False, False, False] * 2,
                [False, False, False, True] * 2,
                [False, False, True, False] * 2,
                [False, False, True, True] * 2,
                [False, True, False, False] * 2,
                [False, True, False, True] * 2,
                [False, True, True, False] * 2,
                [False, True, True, True] * 2,
                [True, False, False, False] * 2,
                [True, False, False, True] * 2,
                [True, False, True, False] * 2,
                [True, False, True, True] * 2,
                [True, True, False, False] * 2,
                [True, True, False, True] * 2,
                [True, True, True, False] * 2,
                [True, True, True, True] * 2,
            ],
        )

    def test_too_big_truth(self):
        f = "def test(a: Qint12) -> Qint12:\n\treturn a"
        qf = qlassf(f, to_compile=False)
        self.assertRaises(Exception, lambda: qf.truth_table())
