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
from ..ast2logic.typing import Arg, Args, BoolExpList
from . import Compiler, CompilerException


def count_symbol_in_expr(expr, d={}):
    for arg in expr.args:
        if isinstance(arg, Symbol):
            # print(arg)
            if arg.name not in d:
                d[arg.name] = 0
            d[arg.name] += 1
        else:
            d = count_symbol_in_expr(arg, d)
    return d


def count_symbols_in_exprs(exprs):
    d = {}
    for s, e in exprs:
        # print(s,e)
        d = count_symbol_in_expr(e, d)
        # print(d)
    return d


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


class POCCompiler3(Compiler):
    """POC2 compiler translating an expression list to quantum circuit"""

    def garbage_collect(self, qc):
        uncomputed = qc.uncompute()
        self.expqmap.remove_map_by_qubits(uncomputed)

    def compile(self, name, args: Args, returns: Arg, exprs: BoolExpList) -> QCircuit:
        exprs = [(symb, self._symplify_exp(exp)) for symb, exp in exprs]

        qc = QCircuit(name=name)

        for arg in args:
            for arg_b in arg.bitvec:
                qc.add_qubit(arg_b)

        self.symbol_count = count_symbols_in_exprs(exprs)
        self.expqmap = ExpQMap()

        for sym, exp in exprs:
            # print(sym, self._symplify_exp(exp))
            iret = self.compile_expr(qc, exp)
            # print("iret", iret)
            qc.map_qubit(sym, iret, promote=True)

            self.garbage_collect(qc)

        return qc

    def compile_expr(self, qc: QCircuit, expr: Boolean) -> int:  # noqa: C901
        if isinstance(expr, Symbol):
            if expr.name in self.symbol_count and self.symbol_count[expr.name] > 0:
                self.symbol_count[expr.name] -= 1
            return qc[expr.name]

        elif expr in self.expqmap:
            for s, c in count_symbol_in_expr(expr, {}).items():
                self.symbol_count[s] -= c

            return self.expqmap[expr]

        elif (
            isinstance(expr, Not)
            and isinstance(expr.args[0], Symbol)
            and self.symbol_count[expr.args[0].name] <= 1
        ):
            print("called not simp")
            self.symbol_count[expr.args[0].name] = 0
            eret = self.compile_expr(qc, expr.args[0])
            qc.x(eret)
            self.expqmap.update_exp_for_qubit(expr, eret)
            return eret

        elif isinstance(expr, Xor) and any(
            [
                isinstance(e, Symbol) and self.symbol_count[e.name] <= 1
                for e in expr.args
            ]
        ):
            print("called xor simp")
            erets = []

            for e in expr.args:
                if isinstance(e, Symbol) and self.symbol_count[e.name] == 1:
                    last = self.compile_expr(qc, e)
                else:
                    erets.append(self.compile_expr(qc, e))

            for x in erets:
                qc.cx(x, last)

            [qc.mark_ancilla(eret) for eret in erets]
            self.garbage_collect(qc)

            self.expqmap.update_exp_for_qubit(last, expr)
            return last

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
            last = erets.pop()

            qc.barrier("xor")

            if last in qc.ancilla_lst:
                fa = last
                self.expqmap.update_exp_for_qubit(last, expr)
            else:
                fa = qc.get_free_ancilla()

                qc.cx(last, fa)
                qc.mark_ancilla(last)
                self.expqmap[expr] = fa

            for x in erets:
                qc.cx(x, fa)

            [qc.mark_ancilla(eret) for eret in erets]
            self.garbage_collect(qc)

            return fa

        elif isinstance(expr, BooleanFalse):
            return qc.get_free_ancilla()

        elif isinstance(expr, BooleanTrue):
            fa = qc.get_free_ancilla()
            qc.x(fa)
            return fa

        else:
            raise CompilerException(expr)
