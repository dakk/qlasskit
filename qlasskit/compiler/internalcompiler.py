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
from ..boolquant import QuantumBooleanGate
from ..qcircuit import QCircuit, QCircuitEnhanced
from . import Compiler, CompilerException, ExpQMap


class InternalCompiler(Compiler):
    """InternalCompiler translating an expression list to quantum circuit"""

    def compile(
        self, name, args: Args, returns: Arg, exprs: BoolExpList, uncompute=True
    ) -> QCircuit:
        qc = QCircuitEnhanced(name=name)
        self.expqmap = ExpQMap()

        for arg in args:
            for arg_b in arg.bitvec:
                # qi =
                qc.add_qubit(arg_b)
                # qc.ancilla_lst.add(qi)

                # TODO: this is redundant, since we also have qc[]
                # self.expqmap[Symbol(arg_b)] = qi

        a_true = None
        a_false = None

        for sym, exp in exprs:
            is_temp = sym.name[0:2] == "__"
            symp_exp = self._symplify_exp(exp)

            if isinstance(symp_exp, BooleanFalse):
                if not a_false:
                    a_false = qc.add_qubit("FALSE")
                iret = a_false
            elif isinstance(symp_exp, BooleanTrue):
                if not a_true:
                    a_true = qc.add_qubit("TRUE")
                    qc.x(a_true)
                iret = a_true
            # Qubit mapped to another qubit (iff sym.name is a _ret)
            elif isinstance(symp_exp, Symbol) and sym.name.startswith("_ret"):
                iret = qc.add_qubit(sym.name)
                qc.cx(qc[symp_exp.name], iret)
            else:
                iret = self.compile_expr(qc, symp_exp)

            self.expqmap[sym] = iret
            qc.map_qubit(sym, iret, promote=not is_temp)

            # Remove all the temp qubits
            self.expqmap.remove(qc.uncompute())

        qc.remove_identities()
        if uncompute:
            keep = [qc[r] for r in filter(lambda r: r in qc, returns.bitvec)]
            qc.uncompute_all(keep=keep)

        return qc

    def compile_expr(  # noqa: C901
        self, qc: QCircuitEnhanced, expr: Boolean, dest=None
    ) -> int:
        if isinstance(expr, Symbol):
            if expr.name in qc:
                return qc[expr.name]
            elif expr.name == "new_qubit":
                return qc.get_free_ancilla()
            else:
                raise CompilerException(f"Symbol not found in qc: {expr.name}")

        elif expr in self.expqmap:
            return self.expqmap[expr]

        elif isinstance(expr, Xor):
            d = qc.get_free_ancilla()

            for e in expr.args:
                if isinstance(e, Symbol):
                    qc.cx(qc[e], d)
                else:
                    d2 = self.compile_expr(qc, e)
                    qc.cx(d2, d)

            self.expqmap[expr] = d
            return d

        elif isinstance(expr, Not):
            eret = self.compile_expr(qc, expr.args[0])

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

            qc.mcx(erets, dest)

            [qc.mark_ancilla(eret) for eret in erets]
            self.expqmap[expr] = dest

            return dest

        # Hybrid Quantum-Boolean circuit
        elif isinstance(expr, QuantumBooleanGate):
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))  # type: ignore
            gate = expr.__class__.__name__.lower()

            if hasattr(qc, gate):
                if gate[0] == "m":
                    getattr(qc, gate)(erets[0:-1], erets[-1])
                else:
                    getattr(qc, gate)(*erets)

                return erets[-1]

            raise Exception(f"Unknown gate: {gate}")

        else:
            raise CompilerException(expr)
