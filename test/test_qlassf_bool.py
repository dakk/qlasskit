import unittest

from sympy import Symbol, symbols
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from qlasskit import QlassF, exceptions, qlassf

a, b, c, d = symbols("a,b,c,d")
_ret = Symbol("_ret")


class TestQlassfBoolean(unittest.TestCase):
    def test_constant_result(self):
        f = "def test() -> bool:\n\treturn True"
        self.assertRaises(exceptions.ConstantReturnException, lambda f: qlassf(f), f)

    def test_unbound(self):
        f = "def test() -> bool:\n\treturn a"
        self.assertRaises(exceptions.UnboundException, lambda f: qlassf(f), f)

    def test_no_return_type(self):
        f = "def test(a: bool):\n\treturn a"
        self.assertRaises(exceptions.NoReturnTypeException, lambda f: qlassf(f), f)

    def test_arg(self):
        ex = a
        f = "def test(a: bool) -> bool:\n\treturn a"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_not_arg(self):
        ex = Not(a)
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_and(self):
        ex = And(Not(a), b)
        f = "def test(a: bool, b: bool) -> bool:\n\treturn not a and b"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_or(self):
        ex = Or(Not(a), b)
        f = "def test(a: bool, b: bool) -> bool:\n\treturn not a or b"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_multiple_arg(self):
        ex = And(a, And(Not(b), c))
        f = "def test(a: bool, b: bool, c: bool) -> bool:\n\treturn a and (not b) and c"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_multiple_arg2(self):
        ex = And(a, And(Not(b), Or(a, c)))
        f = "def test(a: bool, b: bool, c: bool) -> bool:\n\treturn a and (not b) and (a or c)"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_ifexp(self):
        ex = ITE(a, true, false)
        f = "def test(a: bool) -> bool:\n\treturn True if a else False"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    def test_ifexp2(self):
        ex = ITE(And(a, And(Not(b), c)), true, false)
        f = "def test(a: bool, b: bool, c: bool) -> bool:\n\treturn True if a and (not b) and c else False"
        qf = qlassf(f)
        self.assertEqual(len(qf.expressions), 1)
        self.assertEqual(qf.expressions[0][0], _ret)
        self.assertEqual(qf.expressions[0][1], ex)

    # TODO: ITE compile, not yet implemented
    # def test_ifexp3(self):
    #     f = "def test2(a: bool, b: bool, c: bool) -> bool:\n\treturn (c and not b) if a and ((not b) and c) else (a and not c)"
    #     qf = qlassf(f)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     self.assertEqual(
    #         qf.expressions[0][1],
    #         ITE(
    #             And(a, And(Not(b), c)),
    #             And(c, Not(b)),
    #             And(a, Not(c)),
    #         ),
    #     )

    # TODO: assign not yet implemented
    # def test_assign(self):
    #     f = "def test(a: bool, b: bool) -> bool:\n\tc = a and b\n\treturn c"
    #     qf = qlassf(f)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     self.assertEqual(
    #         qf.expressions[0][1],
    #
    #     )

    # def test_assign2(self):
    #     f = (
    #         "def test(a: bool, b: bool, c: bool) -> bool:\n"
    #         + "\td = a and (not b) and c\n"
    #         + "\treturn True if d else False"
    #     )
    #     qf = qlassf(f)
    #     self.assertEqual(len(qf.expressions), 1)
    #     self.assertEqual(qf.expressions[0][0], _ret)
    #     self.assertEqual(
    #         qf.expressions[0][1],

    #     )
