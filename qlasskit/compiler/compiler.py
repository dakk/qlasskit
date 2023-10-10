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


from sympy import Symbol
from sympy.logic import ITE, And, Implies, Not, Or, Xor, simplify_logic
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from .. import QCircuit
from ..ast2logic.typing import Args, BoolExpList


class CompilerException(Exception):
    pass


def optimizer(expr: Boolean) -> Boolean:
    if isinstance(expr, Symbol):
        return expr

    elif isinstance(expr, ITE):
        c = optimizer(expr.args[0])
        return Or(And(c, optimizer(expr.args[1])), And(Not(c), optimizer(expr.args[2])))

    elif isinstance(expr, Implies):
        return Or(Not(optimizer(expr.args[0])), optimizer(expr.args[1]))

    elif isinstance(expr, Not):
        return Not(optimizer(expr.args[0]))

    elif isinstance(expr, And):
        return And(*[optimizer(e) for e in expr.args])

    # Or(And(a,b), And(!a,!b)) = !Xor(a,b)
    elif (
        isinstance(expr, Or)
        and len(expr.args) == 2
        and isinstance(expr.args[0], And)
        and isinstance(expr.args[1], And)
        and expr.args[1].args[0] == Not(expr.args[0].args[0])
        and expr.args[1].args[1] == Not(expr.args[0].args[1])
    ):
        a = optimizer(expr.args[0].args[0])
        b = optimizer(expr.args[0].args[1])
        return Not(Xor(a, b))

    # Translate or to and
    elif isinstance(expr, Or):
        return Not(And(*[Not(optimizer(e)) for e in expr.args]))

    elif isinstance(expr, Xor):
        return Xor(*[optimizer(e) for e in expr.args])

    elif isinstance(expr, BooleanFalse) or isinstance(expr, BooleanTrue):
        raise CompilerException("Constant in expression is not allowed")

    else:
        return expr


class Compiler:
    def __init__(self):
        self.qmap = {}

    def _symplify_exp(self, exp):
        exp = simplify_logic(exp)
        exp = optimizer(exp)
        print("exp3", exp)
        return exp

    def compile(
        self, name: str, args: Args, ret_size: int, expr: BoolExpList
    ) -> QCircuit:
        raise Exception("abstract")
