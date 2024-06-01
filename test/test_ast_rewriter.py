# Copyright 2023-204 Davide Gessa

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
import unittest

from qlasskit.ast2ast import ASTRewriter


class TestASTRewriter(unittest.TestCase):

    def setUp(self):
        self.rewriter = ASTRewriter()

    def test_exponentiation_transformation(self):
        # Test case for a ** 3
        code = "a = b ** 3"
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)

        # Expected transformation
        expected_code = "a = b * b * b"
        expected_tree = ast.parse(expected_code)

        self.assertEqual(ast.dump(new_tree), ast.dump(expected_tree))

    def test_non_exponentiation(self):
        # Test case for non-exponentiation
        code = "a = b + 3"
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)

        # Expected transformation (should be the same)
        expected_code = "a = b + 3"
        expected_tree = ast.parse(expected_code)

        self.assertEqual(ast.dump(new_tree), ast.dump(expected_tree))

    def test_exponentiation_with_non_constant(self):
        # Test case for a ** b (non-constant exponent)
        code = "a = b ** c"
        tree = ast.parse(code)
        new_tree = self.rewriter.visit(tree)

        # Expected transformation (should be the same)
        expected_code = "a = b ** c"
        expected_tree = ast.parse(expected_code)

        self.assertEqual(ast.dump(new_tree), ast.dump(expected_tree))


if __name__ == "__main__":
    unittest.main()
