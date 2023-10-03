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
        self.assertEqual(c, ["a"])

    def test_qint2(self):
        f = "a: Qint2"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, ["a.0", "a.1"])

    def test_qint4(self):
        f = "a: Qint4"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, ["a.0", "a.1", "a.2", "a.3"])

    def test_tuple(self):
        f = "a: Tuple[bool, bool]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, ["a.0", "a.1"])

    def test_tuple_of_tuple(self):
        f = "a: Tuple[Tuple[bool, bool], bool]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, ["a.0.0", "a.0.1", "a.1"])

    def test_tuple_of_tuple2(self):
        f = "a: Tuple[bool, Tuple[bool, bool]]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(c, ["a.0", "a.1.0", "a.1.1"])

    def test_tuple_of_int2(self):
        f = "a: Tuple[Qint2, Qint2]"
        ann_ast = ast.parse(f).body[0].annotation
        c = ast2logic.translate_argument(ann_ast, "a")
        self.assertEqual(
            c,
            [
                "a.0.0",
                "a.0.1",
                "a.1.0",
                "a.1.1",
            ],
        )
