# Copyright 2023-2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import sys
import unittest

from parameterized import parameterized

from qlasskit.ast2ast import ASTRewriter, ConstantFolder


class AddKind(ast.NodeTransformer):
    def visit_Constant(self, n):
        n.kind = None
        return n


def add_kind(n):
    if sys.version_info >= (3, 9):
        return n

    return AddKind().visit(n)


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
        self.assertEqual(ast.dump(add_kind(new_tree)), ast.dump(expected_tree))

    def test_exponentiation_with_zero(self):
        code = "a = b ** 0"
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)

        self.assertTrue(len(new_tree.body), 1)
        self.assertTrue(isinstance(new_tree.body[0], ast.Assign))
        self.assertTrue(isinstance(new_tree.body[0].value, ast.Constant))
        self.assertEqual(new_tree.body[0].value.value, 1)

        if sys.version_info >= (3, 9):
            expected_code = "a = 1"
            expected_tree = ast.parse(expected_code)
            self.assertEqual(ast.dump(add_kind(new_tree)), ast.dump(expected_tree))


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
        self.assertEqual(ast.dump(add_kind(new_tree)), ast.dump(expected_tree))
