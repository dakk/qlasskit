import ast
import unittest

from qlasskit import ast2logic, exceptions


class TestAst2Logic_translate_argument(unittest.TestCase):
    def test_unknown_type(self):
        f = "a: UnknownType"
        ann_ast = ast.parse(f).body[0].annotation
        self.assertRaises(
            exceptions.UnknownTypeException,
            lambda ann_ast: ast2logic.translate_argument(ann_ast, "a"),
            ann_ast,
        )

    def test_bool(self):
        f = "a: bool"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, [("a", "bool")])

    def test_qint2(self):
        f = "a: Qint2"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, [("a.0", "bool"), ("a.1", "bool")])

    def test_qint4(self):
        f = "a: Qint4"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(
            c, [("a.0", "bool"), ("a.1", "bool"), ("a.2", "bool"), ("a.3", "bool")]
        )

    def test_tuple(self):
        f = "a: Tuple[bool, bool]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, [("a.0", "bool"), ("a.1", "bool")])

    def test_tuple_of_tuple(self):
        f = "a: Tuple[Tuple[bool, bool], bool]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, [("a.0.0", "bool"), ("a.0.1", "bool"), ("a.1", "bool")])

    def test_tuple_of_tuple2(self):
        f = "a: Tuple[bool, Tuple[bool, bool]]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, [("a.0", "bool"), ("a.1.0", "bool"), ("a.1.1", "bool")])

    def test_tuple_of_int2(self):
        f = "a: Tuple[Qint2, Qint2]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(
            c,
            [
                ("a.0.0", "bool"),
                ("a.0.1", "bool"),
                ("a.1.0", "bool"),
                ("a.1.1", "bool"),
            ],
        )
