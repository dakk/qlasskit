# Copyright 2023 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License..

from sympy import Symbol
from sympy.logic import And, Not, Or
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from .. import QCircuit
from ..ast2logic.typing import Args, BoolExpList
from . import Compiler, CompilerException


class POCCompiler2(Compiler):
    """POC2 compiler translating an expression list to quantum circuit"""

    def compile(self, name, args: Args, ret_size: int, exprs: BoolExpList) -> QCircuit:
        self.mapped_not = {}
        qc = QCircuit(name=name)

        for arg in args:
            for arg_b in arg.bitvec:
                qc.add_qubit(arg_b)

        for sym, exp in exprs:
            print(sym, exp, self._symplify_exp(exp))
            iret = self.compile_expr(qc, self._symplify_exp(exp))
            print("iret", iret)
            qc.map_qubit(sym, iret, promote=True)
            qc.uncompute2()

        return qc

    def compile_expr(self, qc: QCircuit, expr: Boolean) -> int:
        if isinstance(expr, Symbol):
            return qc[expr.name]

        elif (
            isinstance(expr, Not)
            and isinstance(expr.args[0], Symbol)
            and expr.args[0] in self.mapped_not
        ):
            return self.mapped_not[expr.args[0]]

        elif isinstance(expr, Not):
            fa = qc.get_free_ancilla()
            eret = self.compile_expr(qc, expr.args[0])

            qc.barrier("not")

            qc.cx(eret, fa)
            qc.x(fa)

            qc.uncompute2()

            qc.mark_ancilla(eret)
            # qc.free_ancilla(eret)

            if isinstance(expr.args[0], Symbol):
                self.mapped_not[expr.args[0]] = fa

            return fa

        elif isinstance(expr, And):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            fa = qc.get_free_ancilla()

            qc.barrier("and")

            qc.mcx(erets, fa)

            qc.uncompute2()

            [qc.mark_ancilla(eret) for eret in erets]
            # qc.free_ancillas(erets)

            return fa

        elif isinstance(expr, Or):
            # Translate or to and
            expr = Not(And(*[Not(e) for e in expr.args]))
            print("trans", expr)
            return self.compile_expr(qc, expr)

        # OLD TRANSLATOR
        # elif isinstance(expr, Or):
        #     nclau = len(expr.args)
        #     iclau = list(map(lambda e: self.compile_expr(qc, e), expr.args))
        #     fa = qc.get_free_ancilla()

        #     for i in range(nclau):
        #         for j in range(i + 1, nclau - i):
        #             qc.x(iclau[j])

        #         qc.mcx(iclau[i:], fa)

        #         for j in range(i + 1, nclau - i):
        #             qc.x(iclau[j])

        #     qc.free_ancillas(iclau)

        #     return fa

        elif isinstance(expr, BooleanFalse) or isinstance(expr, BooleanTrue):
            raise CompilerException("Constant in expression is not allowed")

        else:
            raise CompilerException(expr)
