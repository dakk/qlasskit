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
from sympy.logic import And, Not, Xor
from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue

from ..ast2logic.typing import Arg, Args, BoolExpList
from ..boolquant import QuantumBooleanGate
from ..qcircuit import QCircuit, QCircuitEnhanced
from . import Compiler, CompilerException, ExpQMap


class InternalCompiler(Compiler):
    """InternalCompiler translating an expression list to quantum circuit"""

    def compile(  # noqa: C901
        self, name, args: Args, returns: Arg, exprs: BoolExpList, uncompute=True
    ) -> QCircuit:
        qc = QCircuitEnhanced(name=name)
        self.expqmap = ExpQMap()

        # 1. We first add a qubit for every input bit
        input_symbols = [arg_b for arg in args for arg_b in arg.bitvec]
        [qc.add_qubit(arg) for arg in input_symbols]

        # 2. We store here qubit index for the true/false value if required (constant return)
        a_true = None
        a_false = None

        # 3. Iterate over all expressions; iret contains qubit index for the current exp
        for sym, exp in exprs:
            is_temp = sym.name[0:2] == "__"
            symp_exp = self._symplify_exp(exp)

            # 3.1 If we have a constant expression, create if needed and return a constant qubit
            if isinstance(symp_exp, BooleanFalse):
                if not a_false:
                    a_false = qc.add_qubit("FALSE")
                iret = a_false
            elif isinstance(symp_exp, BooleanTrue):
                if not a_true:
                    a_true = qc.add_qubit("TRUE")
                    qc.x(a_true)
                iret = a_true

            # 3.2 If a qubit is mapped to another qubit (iff sym.name is a _ret)
            elif isinstance(symp_exp, Symbol) and sym.name.startswith("_ret"):
                # 3.2.1 Xor mapping to a new qubit if the expr is an input
                if symp_exp.name in input_symbols:
                    iret = qc.add_qubit(sym.name)
                    qc.cx(qc[symp_exp.name], iret)
                # 3.2.2 Remap otherwise
                else:
                    iret = qc[symp_exp.name]

            # 3.3 Self-not (a = ~a)
            elif (
                isinstance(symp_exp, Not)
                and isinstance(symp_exp.args[0], Symbol)
                and symp_exp.args[0].name == sym.name
            ):
                iret = qc[sym.name]
                qc.x(iret)

            # 3.4 Otherwise call compile_expr
            else:
                iret = self.compile_expr(qc, symp_exp)

            # 3.5 Map iret qubit to the symbol
            self.expqmap[sym] = iret
            qc.map_qubit(sym, iret, promote=not is_temp)

            # 3.6 Remove all the temp qubits
            self.expqmap.remove(qc.uncompute())

        # 4. Remove identities gates (ie: X - X)
        qc.remove_identities()

        # 5. Uncompute qubits
        if uncompute and (returns is not None):
            keep = [qc[r] for r in filter(lambda r: r in qc, returns.bitvec)]
            qc.uncompute_all(keep=keep)

        return qc

    def compile_expr(  # noqa: C901
        self, qc: QCircuitEnhanced, expr: Boolean, dest=None
    ) -> int:
        """Compile a boolean expression, return the result qubit"""

        # 1. If expr is a symbol, returns its index
        if isinstance(expr, Symbol):
            if expr.name not in qc:
                raise CompilerException(f"Symbol not found in qc: {expr.name}")

            return qc[expr.name]

        # 2. If expr is already been computed, return its index
        elif expr in self.expqmap:
            return self.expqmap[expr]

        # 3. Special mappings section
        # Add here special expressions mappings to QC

        # (a & b) ^ (a ^ b) & c => MCX(a,b,new), MCX(b,c,new)

        # End of speccial mappings section

        # 4. If expr is a XOR,
        elif isinstance(expr, Xor):
            # 4.1 Get the destination qubit
            d = dest if dest is not None else qc.get_free_ancilla()

            # 4.2 For every arg,
            for e in expr.args:
                # 4.2.1 If it's a symbol, and it's the computed dest, skip
                if isinstance(e, Symbol) and qc[e] == d:
                    continue
                # 4.2.2 If it's a symbol, perform d = d XOR the_symbol
                elif isinstance(e, Symbol):
                    qc.cx(qc[e], d)
                # 4.2.3 If it's an Hybrid quantum classical, compile it and xor
                elif isinstance(e, QuantumBooleanGate):
                    d2 = self.compile_expr(qc, e)
                    qc.cx(d2, d)
                # 4.2.4 If it's a Not of a symbol,
                elif isinstance(e, Not) and not isinstance(
                    e.args[0], Symbol
                ):  # fixes edge case:
                    d = self.compile_expr(qc, e.args[0], dest=d)
                    qc.x(d)
                # 4.2.5 Otherwise compile the expression
                else:
                    d = self.compile_expr(qc, e, dest=d)

            self.expqmap[expr] = d
            return d

        # 5. If expr is a Not,
        elif isinstance(expr, Not):
            # 5.1 Compile the expression
            eret = self.compile_expr(qc, expr.args[0])

            # 5.2 If the expression is on an ancilla, perform the X updating the exp
            if eret in qc.ancilla_lst:
                qc.x(eret)
                self.expqmap[expr] = eret
                return eret
            # 5.3 Otherwise map to a new qubit and perform the X
            else:
                if dest is None:
                    dest = qc.get_free_ancilla()
                qc.cx(eret, dest)
                qc.x(dest)
                qc.mark_ancilla(eret)
                self.expqmap[expr] = dest

                return dest

        # 6. If expr is an And
        elif isinstance(expr, And):
            # 6.1 Compile every argument
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))

            # 6.2 Get a destination qubit
            if dest is None:
                dest = qc.get_free_ancilla()

            # 6.3 If dest is one of the argument, remove from the list
            if dest in erets:
                erets.remove(dest)

            # 6.4 Perform the MCX between all args
            erets = list(set(erets))
            qc.mcx(erets, dest)

            # 6.5 Mark ancilla every argument and return
            [qc.mark_ancilla(eret) for eret in erets]
            self.expqmap[expr] = dest

            return dest

        # 7. If expr is a Hybrid Quantum-Boolean gate
        elif isinstance(expr, QuantumBooleanGate):
            # 7.1 Compile every argument
            erets = list(map(lambda e: self.compile_expr(qc, e), expr.args))  # type: ignore
            gate = expr.__class__.__name__.lower()

            # 7.2 Apply the gate
            if hasattr(qc, gate):
                if gate[0] == "m":
                    getattr(qc, gate)(erets[0:-1], erets[-1])
                else:
                    getattr(qc, gate)(*erets)

                return erets[-1]

            raise Exception(f"Unknown gate: {gate}")

        # 8. Other type of expressions are not allowed
        else:
            raise CompilerException(expr)
