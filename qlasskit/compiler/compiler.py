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


from sympy import simplify, symbols
from sympy.logic import ITE, And, Implies, Not, Or, boolalg

from .. import QCircuit
from ..ast2logic.typing import Args, BoolExpList


class CompilerException(Exception):
    pass


class Compiler:
    def __init__(self):
        self.qmap = {}

    def _symplify_exp(self, exp):
        A, B, C = symbols("A, B, C")
        # Convert Implies to Or
        exp = exp.subs(Implies(A, B), Or(Not(A), B))

        # Convert ITE to And and Or
        exp = exp.subs(ITE(A, B, C), Or(And(A, B), And(Not(A), C)))

        # Simplify the expression
        exp = simplify(exp)
        exp = boolalg.to_cnf(exp)
        return exp

    def compile(
        self, name: str, args: Args, ret_size: int, expr: BoolExpList
    ) -> QCircuit:
        raise Exception("abstract")
