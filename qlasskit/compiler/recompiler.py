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

from sympy import Symbol
from sympy.logic import Not, Xor
from sympy.logic.boolalg import Boolean

from ..ast2logic.typing import Arg, Args, BoolExpList
from ..qcircuit import QCircuit, QCircuitEnhanced
from . import Compiler, CompilerException


class ReCompiler(Compiler):
    """ReCompiler translating decompiled expressions to quantum circuit"""

    def compile(  # noqa: C901
        self,
        name: str,
        args: Args,
        returns: Arg,
        exprs: BoolExpList,
        uncompute: bool = True,
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
