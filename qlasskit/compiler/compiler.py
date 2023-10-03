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

from typing import Tuple

from sympy import Symbol, simplify, symbols
from sympy.logic import ITE, And, Implies, Not, Or, boolalg
from sympy.logic.boolalg import Boolean

from .. import QCircuit
from ..typing import Args, BoolExpList


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

    def compile(self, args: Args, ret_size: int, expr: BoolExpList) -> QCircuit:
        raise Exception("abstract")


class MultipassCompiler(Compiler):
    pass


class POCCompiler(Compiler):
    """POC compiler translating an expression list to quantum circuit"""

    def compile(self, args: Args, ret_size: int, exprs: BoolExpList) -> QCircuit:
        qc = QCircuit()
        self.qmap = {}

        for sym, exp in exprs:
            iret, qc = self.compile_expr(qc, self._symplify_exp(exp))
            self.qmap[sym] = iret

        return qc

    def compile_expr(
        self, qc: QCircuit, expr: Boolean
    ) -> Tuple[int, QCircuit]:  # noqa: C901
        # match expr:
        if isinstance(expr, Symbol):
            if expr.name not in self.qmap:
                self.qmap[expr.name] = len(self.qmap)
                qc.add_qubit()
            return self.qmap[expr.name], qc

        elif isinstance(expr, Not):
            i, qc = self.compile_expr(qc, expr.args[0])
            qc.x(i)
            return i, qc

        elif isinstance(expr, And):
            il = []

            for x in expr.args:
                ii, qc = self.compile_expr(qc, x)
                il.append(ii)

            iold = il[0]
            for x in range(1, len(il)):
                inew = len(self.qmap)
                qc.add_qubit()
                self.qmap[f"anc_{len(self.qmap)}"] = inew
                qc.ccx(iold, il[x], inew)
                iold = inew

            return inew, qc

        elif isinstance(expr, Or):
            if len(expr.args) > 2:
                raise Exception("too many clause")

            i1, qc = self.compile_expr(qc, expr.args[0])
            i2, qc = self.compile_expr(qc, expr.args[1])
            i3 = len(self.qmap)
            qc.add_qubit()
            self.qmap[f"anc_{len(self.qmap)}"] = i3

            qc.x(i2)
            qc.ccx(i1, i2, i3)
            qc.x(i2)
            qc.cx(i2, i3)
            return i3, qc

        elif isinstance(expr, boolalg.BooleanFalse) or isinstance(
            expr, boolalg.BooleanTrue
        ):
            raise CompilerException("Constant in expression is not allowed")

        else:
            raise Exception(expr)


def to_quantum(args, ret_size, exprs, compiler="poc"):
    if compiler == "multipass":
        s = MultipassCompiler()
    elif compiler == "poc":
        s = POCCompiler()

    circ = s.compile(args, ret_size, exprs)
    return circ
