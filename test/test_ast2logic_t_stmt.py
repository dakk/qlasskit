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

import ast
import unittest

from qlasskit import ast2logic, exceptions


class TestAst2Logic_translate_statement(unittest.TestCase):
    def test_statement_not_handled(self):
        f = "continue"
        e = ast.parse(f)

        self.assertRaises(
            exceptions.StatementNotHandledException,
            lambda e: ast2logic.translate_statement(e, {}, bool),
            e,
        )
