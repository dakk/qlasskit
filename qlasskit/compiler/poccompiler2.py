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

from typing import Dict

from sympy import Symbol
from sympy.logic import And, Not, Xor
from sympy.logic.boolalg import Boolean

from .. import QCircuit
from ..ast2logic.typing import Args, BoolExpList
from . import Compiler, CompilerException


class POCCompiler2(Compiler):
    """POC2 compiler translating an expression list to quantum circuit"""

    def garbage_collect(self, qc):
        uncomputed = qc.uncompute()

        for k in self.mapped.keys():
            if self.mapped[k] in uncomputed:
                del self.mapped[k]

    def compile(self, name, args: Args, ret_size: int, exprs: BoolExpList) -> QCircuit:
        qc = QCircuit(name=name)

        for arg in args:
            for arg_b in arg.bitvec:
                qc.add_qubit(arg_b)

        self.mapped: Dict[Boolean, int] = {}

        for sym, exp in exprs:
            # print(sym, self._symplify_exp(exp))
            iret = self.compile_expr(qc, self._symplify_exp(exp))
            # print("iret", iret)
            qc.map_qubit(sym, iret, promote=True)

            self.garbage_collect(qc)

        return qc

    def compile_expr(self, qc: QCircuit, expr: Boolean) -> int:
        if isinstance(expr, Symbol):
            return qc[expr.name]

        elif expr in self.mapped:
            # print("!!cachehit!!", expr)
            return self.mapped[expr]

        elif isinstance(expr, Not):
            fa = qc.get_free_ancilla()
            eret = self.compile_expr(qc, expr.args[0])

            qc.barrier("not")

            qc.cx(eret, fa)
            qc.x(fa)

            qc.mark_ancilla(eret)
            self.garbage_collect(qc)

            self.mapped[expr] = fa

            return fa

        elif isinstance(expr, And):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            fa = qc.get_free_ancilla()

            qc.barrier("and")

            qc.mcx(erets, fa)

            [qc.mark_ancilla(eret) for eret in erets]

            self.garbage_collect(qc)

            self.mapped[expr] = fa

            return fa

        elif isinstance(expr, Xor):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            qc.mcx(erets[0:-1], erets[-1])
            return erets[-1]

        else:
            raise CompilerException(expr)
