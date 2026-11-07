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

import ast
import unittest

from parameterized import parameterized

from qlasskit.ast2ast import ASTRewriter, ConstantFolder


class AddKind(ast.NodeTransformer):
    def visit_Constant(self, n):
        n.kind = None
        return n


class TestASTRewriter(unittest.TestCase):

    def setUp(self):
        self.rewriter = ASTRewriter()

    @parameterized.expand(
        [
            ("a = b ** 3", "a = b * b * b"),
            ("a = b + 3", "a = b + 3"),
            ("a = b ** c", "a = b ** c"),
        ]
    )
    def test_exponentiation_transformation(self, code, expected_code):
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)
        expected_tree = ast.parse(expected_code)
        self.assertEqual(ast.dump(new_tree), ast.dump(expected_tree))

    def test_exponentiation_with_zero(self):
        code = "a = b ** 0"
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)

        self.assertTrue(len(new_tree.body), 1)
        self.assertTrue(isinstance(new_tree.body[0], ast.Assign))
        self.assertTrue(isinstance(new_tree.body[0].value, ast.Constant))
        self.assertEqual(new_tree.body[0].value.value, 1)

        expected_code = "a = 1"
        expected_tree = ast.parse(expected_code)
        self.assertEqual(ast.dump(new_tree), ast.dump(expected_tree))


class TestASTConstantFolder(unittest.TestCase):
    def setUp(self):
        self.rewriter = ConstantFolder()

    @parameterized.expand(
        [
            ("a + (13 - 12 + 1)", "a + 2"),
            # ( "a + 13 - 12 + 1", "a + 2" ),
            ("a + len([12])", "a + 1"),
            ("if True: a \nelse: b", "a"),
            ("a if False else b", "b"),
        ]
    )
    def test_expected_code(self, code, expected_code):
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)
        expected_tree = ast.parse(expected_code)
        self.assertEqual(ast.dump(new_tree), ast.dump(expected_tree))
