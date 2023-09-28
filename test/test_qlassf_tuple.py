import unittest
from typing import Tuple

from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")
a_0 = Symbol("a.0")
a_1 = Symbol("a.1")
b_0 = Symbol("b.0")
b_1 = Symbol("b.1")


class TestQlassfTuple(unittest.TestCase):
    def test_tuple_arg(self):
        f = "def test(a: Tuple[bool, bool]) -> bool:\n\treturn a[0] and a[1]"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], And(a_0, a_1))

    def test_tuple_arg_assign(self):
        f = (
            "def test(a: Tuple[bool, bool]) -> bool:\n"
            + "\tb = a[0]\n"
            + "\tc = a[1]\n"
            + "\treturn b and c"
        )
        qf = qlassf(f, to_compile=False)
        self.assertEqual(len(qf.expressions), 3)
        self.assertEqual(qf.expressions[-1][0], _ret)
        self.assertEqual(qf.expressions[-1][1], And(b, c))

    def test_tuple_of_tuple_arg(self):
        f = "def test(a: Tuple[Tuple[bool, bool], bool]) -> bool:\n\treturn a[0][0] and a[0][1] and a[1]"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1], And(Symbol("a.0.0"), And(Symbol("a.0.1"), a_1))
        )

    def test_tuple_of_tuple_of_tuple_arg(self):
        f = (
            "def test(a: Tuple[Tuple[Tuple[bool, bool], bool], bool]) -> bool:\n"
            + "\treturn a[0][0][0] and a[0][0][1] and a[0][1] and a[1]"
        )
        qf = qlassf(f, to_compile=False)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(
            qf.expressions[0][1],
            And(Symbol("a.0.0.0"), And(Symbol("a.0.0.1"), And(Symbol("a.0.1"), a_1))),
        )

    def test_tuple_assign(self):
        f = "def test(a: Tuple[bool, bool]) -> bool:\n\tb = (a[1],a[0])\n\treturn b[0] and b[1]"
        qf = qlassf(f, to_compile=False)
        self.assertEqual(len(qf.expressions), 3)
        self.assertEqual(qf.expressions[-1][0], _ret)
        self.assertEqual(qf.expressions[-1][1], And(b_0, b_1))

    def test_tuple_assign2(self):
        f = (
            "def test(a: Tuple[Tuple[bool, bool], bool]) -> bool:\n"
            + "\tb = (a[0][1],a[0][0],a[1])\n"
            + "\treturn b[0] and b[1] and b[2]"
        )
        qf = qlassf(f, to_compile=False)
        self.assertEqual(len(qf.expressions), 4)
        self.assertEqual(qf.expressions[-1][0], _ret)
        self.assertEqual(qf.expressions[-1][1], And(b_0, And(b_1, Symbol("b.2"))))

    # TODO: qlasskit.exceptions.UnboundException: b.1.0 in {a.0.0: 'bool', a.0.1: 'bool', a.1: 'bool', b.0: 'bool', b.1: 'bool'}
    # def test_tuple_assign3(self):
    #     f = (
    #         "def test(a: Tuple[Tuple[bool, bool], bool]) -> bool:\n"
    #         + "\tb = (a[0][1],(a[0][0],a[1]))\n"
    #         + "\treturn b[0] and b[1][0] and b[1][1]"
    #     )
    #     qf = qlassf(f, to_compile=False)
    #     self.assertEqual(len(qf.expressions), 4)
    #     self.assertEqual(qf.expressions[-1][0], _ret)
    #     self.assertEqual(qf.expressions[-1][1], And(b_0, And(b_1, Symbol("b.2"))))
