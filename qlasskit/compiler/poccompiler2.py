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
from ..typing import Args, BoolExpList
from . import Compiler, CompilerException


class POCCompiler2(Compiler):
    """POC2 compiler translating an expression list to quantum circuit"""

    def compile(self, args: Args, ret_size: int, exprs: BoolExpList) -> QCircuit:
        qc = QCircuit()

        for arg in args:
            qc.add_qubit(arg)

        for sym, exp in exprs:
            iret = self.compile_expr(qc, self._symplify_exp(exp))
            qc.map_qubit(sym, iret)

        return qc

    def compile_expr(self, qc: QCircuit, expr: Boolean) -> int:
        if isinstance(expr, Symbol):
            return qc[expr.name]

        elif isinstance(expr, Not):
            fa = qc.get_free_ancilla()
            eret = self.compile_expr(qc, expr.args[0])
            qc.x(eret)
            qc.cx(eret, fa)
            qc.x(eret)
            return fa

        elif isinstance(expr, And):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            fa = qc.get_free_ancilla()
            qc.mcx(erets, fa)
            return fa

        elif isinstance(expr, Or):
            nclau = len(expr.args)
            iclau = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            fa = qc.get_free_ancilla()

            for i in range(nclau):
                for j in range(i + 1, nclau - i):
                    qc.x(iclau[j])

                qc.mcx(iclau[i:], fa)

                for j in range(i + 1, nclau - i):
                    qc.x(iclau[j])

            return fa

        elif isinstance(expr, BooleanFalse) or isinstance(expr, BooleanTrue):
            raise CompilerException("Constant in expression is not allowed")

        else:
            raise CompilerException(expr)
