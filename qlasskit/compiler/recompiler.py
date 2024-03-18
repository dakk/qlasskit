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

from sympy import Symbol
from sympy.logic import Not, Xor
from sympy.logic.boolalg import Boolean

from ..ast2logic.typing import Arg, Args, BoolExpList
from ..qcircuit import QCircuit, QCircuitEnhanced
from . import Compiler, CompilerException


class ReCompiler(Compiler):
    """ReCompiler translating decompiled expressions to quantum circuit"""

    def compile(  # noqa: C901
        self, name, args: Args, returns: Arg, exprs: BoolExpList, uncompute=True
    ) -> QCircuit:
        qc = QCircuitEnhanced(name=name)
        self.qubit_contains = {}

        for arg in args:
            for arg_b in arg.bitvec:
                qc.add_qubit(arg_b)
                self.qubit_contains[arg_b] = arg_b

        for sym, exp in exprs:
            symp_exp = self._symplify_exp(exp)
            self.compile_expr(qc, sym, symp_exp)

        qc.remove_identities()

        return qc

    def compile_expr(  # noqa: C901
        self, qc: QCircuitEnhanced, sym: Symbol, expr: Boolean
    ):
        # A = A
        if isinstance(expr, Symbol) and expr.name == sym.name:
            pass

        # A = Not (A)
        elif (
            isinstance(expr, Not)
            and isinstance(expr.args[0], Symbol)
            and expr.args[0].name == sym.name
        ):
            qc.x(qc[sym.name])
            self.qubit_contains[sym.name] = Not(sym)

        # A = Not (E)
        elif isinstance(expr, Not):
            print("handling", expr)
            self.compile_expr(qc, sym, expr.args[0])
            qc.x(qc[sym.name])
            self.qubit_contains[sym.name] = expr

        # A = A ^ B
        elif isinstance(expr, Xor) and sym in expr.free_symbols:
            for arg in expr.args:
                if arg.free_symbols == set([sym]):
                    if isinstance(arg, Not):
                        qc.x(qc[sym.name])
                elif isinstance(arg, Symbol):
                    qc.cx(qc[arg.name], qc[sym.name])
                elif isinstance(arg, Not) and isinstance(arg.args[0], Symbol):
                    if isinstance(self.qubit_contains[arg.args[0].name], Symbol):
                        self.compile_expr(qc, arg.args[0], Not(arg.args[0]))
                    qc.cx(qc[arg.args[0].name], qc[sym.name])

            qc[sym.name] = expr

        elif isinstance(expr, Xor):
            self.compile_expr(qc, expr.free_symbols[0], expr)

        else:
            raise CompilerException(expr)
