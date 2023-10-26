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
from sympy.logic import And, Not, Xor
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from ..ast2logic.typing import Arg, Args, BoolExpList
from ..qcircuit import QCircuit, QCircuitEnhanced
from . import Compiler, CompilerException, ExpQMap


def count_symbol_in_expr(expr, d={}):
    for arg in expr.args:
        if isinstance(arg, Symbol):
            if arg.name not in d:
                d[arg.name] = 0
            d[arg.name] += 1
        else:
            d = count_symbol_in_expr(arg, d)
    return d


def count_symbols_in_exprs(exprs):
    d = {}
    for s, e in exprs:
        d = count_symbol_in_expr(e, d)
    return d


class POCCompiler3(Compiler):
    """POC3 compiler translating an expression list to quantum circuit"""

    def garbage_collect(self, qc):
        uncomputed = qc.uncompute()
        self.expqmap.remove(uncomputed)

    def compile(self, name, args: Args, returns: Arg, exprs: BoolExpList) -> QCircuit:
        exprs = [(symb, self._symplify_exp(exp)) for symb, exp in exprs]

        qc = QCircuitEnhanced(name=name)

        for arg in args:
            for arg_b in arg.bitvec:
                qc.add_qubit(arg_b)

        self.symbol_count = count_symbols_in_exprs(exprs)
        self.expqmap = ExpQMap()

        for sym, exp in exprs:
            print(self.symbol_count)
            # print(sym, self._symplify_exp(exp))
            iret = self.compile_expr(qc, exp)
            # print("iret", iret)
            qc.map_qubit(sym, iret, promote=True)

            self.garbage_collect(qc)

            print(sym, exp)
            print(self.symbol_count)
            circ_qi = qc.export("circuit", "qiskit")
            print(circ_qi.draw("text"))
            print()
            print()
        return qc

    def compile_expr(self, qc: QCircuitEnhanced, expr: Boolean) -> int:  # noqa: C901
        if isinstance(expr, Symbol):
            if expr.name in self.symbol_count and self.symbol_count[expr.name] > 0:
                self.symbol_count[expr.name] -= 1
            return qc[expr.name]

        elif expr in self.expqmap:
            print(expr, self.expqmap.exp_map)
            for s, c in count_symbol_in_expr(expr, {}).items():
                self.symbol_count[s] -= c

            return self.expqmap[expr]

        elif (
            isinstance(expr, Not)
            and isinstance(expr.args[0], Symbol)
            and self.symbol_count[expr.args[0].name] == 1
        ):
            print("thegame")
            eret = self.compile_expr(qc, expr.args[0])
            qc.x(eret)
            self.expqmap[expr] = eret
            return eret

        elif isinstance(expr, Xor) and any(
            [
                isinstance(e, Symbol) and self.symbol_count[e.name] == 1
                for e in expr.args
            ]
        ):
            erets = []

            for e in expr.args:
                if isinstance(e, Symbol) and self.symbol_count[e.name] == 1:
                    last = self.compile_expr(qc, e)
                else:
                    erets.append(self.compile_expr(qc, e))

            for x in erets:
                qc.cx(x, last)

            [qc.mark_ancilla(eret) for eret in erets]
            self.expqmap[expr] = last
            return last

        elif isinstance(expr, Not):
            eret = self.compile_expr(qc, expr.args[0])
            qc.barrier("not")

            if eret in qc.ancilla_lst:
                qc.x(eret)
                self.expqmap[expr] = eret
                return eret
            else:
                fa = qc.get_free_ancilla()
                qc.cx(eret, fa)
                qc.x(fa)
                qc.mark_ancilla(eret)
                self.expqmap[expr] = fa

                return fa

        elif isinstance(expr, And):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            fa = qc.get_free_ancilla()
            qc.barrier("and")
            qc.mcx(erets, fa)
            [qc.mark_ancilla(eret) for eret in erets]
            self.expqmap[expr] = fa

            return fa

        elif isinstance(expr, Xor):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            last = erets.pop()
            qc.barrier("xor")

            if last in qc.ancilla_lst:
                fa = last
                self.expqmap[expr] = last
            else:
                fa = qc.get_free_ancilla()
                qc.cx(last, fa)
                qc.mark_ancilla(last)
                self.expqmap[expr] = fa

            for x in erets:
                qc.cx(x, fa)

            [qc.mark_ancilla(eret) for eret in erets]

            return fa

        elif isinstance(expr, BooleanFalse):
            return qc.get_free_ancilla()

        elif isinstance(expr, BooleanTrue):
            fa = qc.get_free_ancilla()
            qc.x(fa)
            return fa

        else:
            raise CompilerException(expr)
