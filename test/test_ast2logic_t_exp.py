import ast
import unittest

from qlasskit import ast2logic, exceptions


class TestAst2Logic_translate_expression(unittest.TestCase):
    def test_expression_not_handled(self):
        f = "true not in true"
        e = ast.parse(f)

        self.assertRaises(
            exceptions.ExpressionNotHandledException,
            lambda e: ast2logic.translate_expression(e, {}),
            e,
        )
