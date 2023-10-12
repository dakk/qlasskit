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
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from .. import QCircuit
from ..ast2logic.typing import Args, BoolExpList
from . import Compiler, CompilerException


class ExpQMap:
    """Mapping between qubit and boolexp and vice-versa"""

    def __init__(self):
        self.exp_map: Dict[Boolean, int] = {}

    def __contains__(self, k):
        return k in self.exp_map

    def __getitem__(self, k):
        return self.exp_map[k]

    def __setitem__(self, k, v):
        self.exp_map[k] = v

    def remove_map_by_qubits(self, qbs):
        todel = []
        for k in self.exp_map.keys():
            if self.exp_map[k] in qbs:
                todel.append(k)

        for k in todel:
            del self.exp_map[k]

    def update_exp_for_qubit(self, qb, exp):
        self.remove_map_by_qubits([qb])
        self[exp] = qb


class POCCompiler2(Compiler):
    """POC2 compiler translating an expression list to quantum circuit"""

    def garbage_collect(self, qc):
        uncomputed = qc.uncompute()
        self.expqmap.remove_map_by_qubits(uncomputed)

    def compile(self, name, args: Args, ret_size: int, exprs: BoolExpList) -> QCircuit:
        qc = QCircuit(name=name)

        for arg in args:
            for arg_b in arg.bitvec:
                qc.add_qubit(arg_b)

        self.expqmap = ExpQMap()

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

        elif expr in self.expqmap:
            return self.expqmap[expr]

        elif isinstance(expr, Not):
            eret = self.compile_expr(qc, expr.args[0])

            qc.barrier("not")

            if eret in qc.ancilla_lst:
                qc.x(eret)
                self.expqmap.update_exp_for_qubit(eret, expr)
                return eret
            else:
                fa = qc.get_free_ancilla()
                qc.cx(eret, fa)
                qc.x(fa)
                qc.mark_ancilla(eret)

                self.garbage_collect(qc)
                self.expqmap[expr] = fa

                return fa

        elif isinstance(expr, And):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            fa = qc.get_free_ancilla()

            qc.barrier("and")

            qc.mcx(erets, fa)

            [qc.mark_ancilla(eret) for eret in erets]

            self.garbage_collect(qc)

            self.expqmap[expr] = fa

            return fa

        elif isinstance(expr, Xor):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))

            qc.barrier("xor")
            [qc.mark_ancilla(eret) for eret in erets[:-1]]

            qc.mcx(erets[0:-1], erets[-1])
            return erets[-1]

        elif isinstance(expr, BooleanFalse):
            return qc.get_free_ancilla()

        elif isinstance(expr, BooleanTrue):
            fa = qc.get_free_ancilla()
            qc.x(fa)
            return fa

        else:
            raise CompilerException(expr)
