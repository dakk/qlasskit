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
from sympy import And, Not, Or, Symbol, symbols
from sympy.logic.boolalg import BooleanTrue

from qlasskit import bool_optimizer

a, b, c, d = symbols("a,b,c,d")
__a0 = Symbol("__a.0")
a0 = Symbol("a.0")
eTrue = And(True)
eFalse = And(False)


@parameterized_class(
    ("exps", "n_exps"),
    [
        ([], []),
        ([(a, eTrue), (b, Or(Not(a), c))], [(b, c)]),
        ([(a, eFalse), (b, And(Not(a), c))], [(b, c)]),
        ([(a, eFalse), (b, Or(Not(a), c))], []),
    ],
)
class TestBoolOptimizer_remove_const_exps(unittest.TestCase):
    def test_remove_const_exps(self):
        n_exps = bool_optimizer.remove_const_exps(self.exps)
        self.assertEqual(self.n_exps, n_exps)


@parameterized_class(
    ("exps", "n_exps"),
    [
        ([], []),
        ([(__a0, a0), (a0, __a0)], []),
        ([(__a0, a0), (d, Not(b)), (a0, __a0)], [(d, Not(b))]),
        (
            [(__a0, a0), (d, Not(__a0)), (a0, __a0)],
            [(__a0, a0), (d, Not(__a0)), (a0, __a0)],
        ),
    ],
)
class TestBoolOptimizer_remove_unnecessary_assigns(unittest.TestCase):
    def test_remove_unnecessary_assigns(self):
        n_exps = bool_optimizer.remove_unnecessary_assigns(self.exps)
        self.assertEqual(self.n_exps, n_exps)


@parameterized_class(
    ("exps", "n_exps"),
    [
        ([], []),
        ([(__a0, Not(a)), (a, __a0)], [(a, Not(a))]),
    ],
)
class TestBoolOptimizer_merge_unnecessary_assigns(unittest.TestCase):
    def test_merge_unnecessary_assigns(self):
        n_exps = bool_optimizer.merge_unnecessary_assigns(self.exps)
        self.assertEqual(self.n_exps, n_exps)
