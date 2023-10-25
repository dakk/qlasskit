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
from sympy.logic import And, Not, Xor
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from .. import QCircuit
from ..ast2logic.typing import Arg, Args, BoolExpList
from . import Compiler, CompilerException, ExpQMap


class POCCompiler2(Compiler):
    """POC2 compiler translating an expression list to quantum circuit"""

    def compile(self, name, args: Args, returns: Arg, exprs: BoolExpList) -> QCircuit:
        qc = QCircuit(name=name)
        self.expqmap = ExpQMap()

        for arg in args:
            for arg_b in arg.bitvec:
                # qi =
                qc.add_qubit(arg_b)
                # qc.ancilla_lst.add(qi)

                # TODO: this is redundant, since we also have qc[]
                # self.expqmap[Symbol(arg_b)] = qi

        for sym, exp in exprs:
            is_temp = sym.name[0:2] == "__"
            symp_exp = self._symplify_exp(exp)

            iret = self.compile_expr(qc, symp_exp)

            self.expqmap[sym] = iret
            qc.map_qubit(sym, iret, promote=not is_temp)

            # Remove all the temp qubits
            self.expqmap.remove(qc.uncompute())

        qc.remove_identities()
        qc.uncompute_all(keep=[qc[r] for r in returns.bitvec])

        # circ_qi = qc.export("circuit", "qiskit")
        # print(circ_qi.draw("text"))
        # print()
        # print()

        return qc

    def compile_expr(self, qc: QCircuit, expr: Boolean, dest=None) -> int:  # noqa: C901
        if isinstance(expr, Symbol) and expr.name in qc:
            return qc[expr.name]

        elif expr in self.expqmap:
            return self.expqmap[expr]

        elif isinstance(expr, Not):
            eret = self.compile_expr(qc, expr.args[0])

            qc.barrier("not")

            if eret in qc.ancilla_lst:
                qc.x(eret)
                self.expqmap[expr] = eret
                return eret
            else:
                if dest is None:
                    dest = qc.get_free_ancilla()
                qc.cx(eret, dest)
                qc.x(dest)
                qc.mark_ancilla(eret)
                self.expqmap[expr] = dest

                return dest

        elif isinstance(expr, And):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            if dest is None:
                dest = qc.get_free_ancilla()

            qc.barrier("and")
            qc.mcx(erets, dest)

            [qc.mark_ancilla(eret) for eret in erets]
            self.expqmap[expr] = dest

            return dest

        elif isinstance(expr, Xor):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))
            last = erets.pop()

            qc.barrier("xor")

            if last in qc.ancilla_lst:
                dest = last
                self.expqmap[expr] = last
            else:
                if dest is None:
                    dest = qc.get_free_ancilla()

                qc.cx(last, dest)
                qc.mark_ancilla(last)
                self.expqmap[expr] = dest

            for x in erets:
                qc.cx(x, dest)

            [qc.mark_ancilla(eret) for eret in erets]
            return dest

        elif isinstance(expr, BooleanFalse):
            return qc.get_free_ancilla()

        elif isinstance(expr, BooleanTrue):
            if dest is None:
                dest = qc.get_free_ancilla()
            qc.x(dest)
            return dest

        else:
            raise CompilerException(expr)
