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

from sympy import Symbol, simplify, symbols
from sympy.logic import ITE, And, Implies, Not, Or, boolalg

from ..typing import BoolExp, BoolExpList


class CompilerException(Exception):
    pass


class CompilerResult:
    def __init__(self, res_qubit, gate_list, qubit_map):
        self.res_qubit = res_qubit
        self.gate_list = gate_list
        self.qubit_map = qubit_map

    @property
    def num_qubits(self):
        return len(self.qubit_map)

    def to_qiskit(self):
        from qiskit import QuantumCircuit

        qc = QuantumCircuit(len(self.qubit_map), 0)

        for g in self.gate_list:
            # match g[0]:
            if g[0] == "x":
                qc.x(g[1])
            elif g[0] == "cx":
                qc.cx(g[1], g[2])
            elif g[0] == "ccx":
                qc.ccx(g[1], g[2], g[3])

        return qc.to_gate()


class Compiler:
    def __init__(self):
        self.qmap = {}

    def _symplify_exp(self, exp):
        A, B, C = symbols("A, B, C")
        # Convert Implies to Or
        exp = exp.subs(Implies(A, B), Or(Not(A), B))

        # Convert ITE to And and Or
        exp = exp.subs(ITE(A, B, C), Or(And(A, B), And(Not(A), C)))

        # Simplify the expression
        exp = simplify(exp)
        exp = boolalg.to_cnf(exp)
        return exp

    def compile(self, expr):
        raise Exception("abstract")


class MultipassCompiler(Compiler):
    pass


class POCCompiler(Compiler):
    """POC compiler translating an expression list to quantum circuit"""

    def compile(self, exprs: BoolExpList):
        self.qmap = {}
        gl = []

        for sym, exp in exprs:
            iret, gates = self.compile_expr(self._symplify_exp(exp))
            gl.extend(gates)
            self.qmap[sym] = iret
            if sym == Symbol("_ret"):  # TODO: this won't work with multiple res
                return iret, gl

    def compile_expr(self, expr: BoolExp):  # noqa: C901
        # match expr:
        if isinstance(expr, Symbol):
            if expr.name not in self.qmap:
                self.qmap[expr.name] = len(self.qmap)
            return self.qmap[expr.name], []

        elif isinstance(expr, Not):
            i, g = self.compile_expr(expr.args[0])
            return i, g + [("x", i)]

        elif isinstance(expr, And):
            il = []
            gl = []

            for x in expr.args:
                ii, gg = self.compile_expr(x)
                il.append(ii)
                gl.extend(gg)

            iold = il[0]
            for x in range(1, len(il)):
                inew = len(self.qmap)
                self.qmap[f"anc_{len(self.qmap)}"] = inew
                gl.append(("ccx", iold, il[x], inew))
                iold = inew

            return inew, gl

        elif isinstance(expr, Or):
            if len(expr.args) > 2:
                raise Exception("too many clause")

            i1, g1 = self.compile_expr(expr.args[0])
            i2, g2 = self.compile_expr(expr.args[1])
            i3 = len(self.qmap)
            self.qmap[f"anc_{len(self.qmap)}"] = i3

            return i3, g1 + g2 + [
                ("x", i2),
                ("ccx", i1, i2, i3),
                ("x", i2),
                ("cx", i2, i3),
            ]

        elif isinstance(expr, boolalg.BooleanFalse) or isinstance(
            expr, boolalg.BooleanTrue
        ):
            raise CompilerException("Constant in expression is not allowed")

        else:
            raise Exception(expr)


def to_quantum(exprs, compiler="poc"):
    if compiler == "multipass":
        s = MultipassCompiler()
    elif compiler == "poc":
        s = POCCompiler()

    res_qubit, gate_list = s.compile(exprs)
    return CompilerResult(res_qubit, gate_list, s.qmap)
