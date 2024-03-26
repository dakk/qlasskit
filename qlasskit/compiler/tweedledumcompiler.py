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

from typing import Dict

from sympy import Symbol
from sympy.logic import And, Not, Or, Xor
from sympy.logic.boolalg import BooleanFalse, BooleanTrue
from tweedledum.classical import LogicNetwork
from tweedledum.ir import Qubit, rotation_angle
from tweedledum.passes import gate_cancellation, linear_resynth, parity_decomp
from tweedledum.synthesis import xag_synth

from .. import QCircuit
from ..ast2logic.typing import Arg, Args, BoolExpList
from ..qcircuit import gates
from . import Compiler


def sympy_to_logic_network(  # noqa: C901
    name, args: Args, returns: Arg, exprs: BoolExpList
) -> LogicNetwork:
    _symbol_table: Dict[str, int] = dict()
    _logic_network = LogicNetwork()

    def _apply(expr, op):
        signals = list(map(visit, expr.args))

        prev_res = signals[0]
        for s in signals[1:]:
            prev_res = getattr(_logic_network, op)(prev_res, s)
        return prev_res

    def visit(expr):
        if isinstance(expr, Symbol):
            return _symbol_table[expr.name]

        elif isinstance(expr, Not):
            signals = list(map(visit, expr.args))
            return _logic_network.create_not(signals[0])

        elif isinstance(expr, And):
            return _apply(expr, "create_and")

        elif isinstance(expr, Or):
            return _apply(expr, "create_or")

        elif isinstance(expr, Xor):
            return _apply(expr, "create_xor")

        elif isinstance(expr, BooleanTrue):
            return _logic_network.get_constant(1)

        elif isinstance(expr, BooleanFalse):
            return _logic_network.get_constant(0)

        else:
            raise Exception(f"Expression {expr} not handled by the tweedledum compiler")

    for arg in args:
        for bv in arg.bitvec:
            pi = _logic_network.create_pi(bv)
            _symbol_table[bv] = pi

    for s, e in exprs:
        v_signal = visit(e)
        _symbol_table[s.name] = v_signal

        if s.name[0:4] == "_ret":
            _logic_network.create_po(v_signal)

    return _logic_network


def twcircuit_to_qcircuit(twc):
    pass


class TweedledumCompiler(Compiler):
    """Compile using tweedledum synthesis library"""

    def compile(  # noqa: C901
        self, name, args: Args, returns: Arg, exprs: BoolExpList, uncompute: bool = True
    ) -> QCircuit:
        if not uncompute:
            raise Exception("Disabled uncompute not supported on tweedledum")

        exprs = [(symb, self._symplify_exp(exp)) for symb, exp in exprs]
        _logic_network = sympy_to_logic_network(name, args, returns, exprs)

        sy = xag_synth(_logic_network)
        sy = parity_decomp(sy)
        sy = gate_cancellation(sy)
        sy = linear_resynth(sy)

        # print(sy)

        qc = QCircuit(sy.num_qubits(), native=sy)

        ri = 0
        for arg in args:
            for bv in arg.bitvec:
                qc[bv] = ri
                ri += 1

        for bv in returns.bitvec:
            qc[bv] = ri
            ri += 1

        for instruction in sy:
            qubits = [
                (qubit.uid(), qubit.polarity() == Qubit.Polarity.positive)
                for qubit in instruction.qubits()
            ]
            op = instruction.kind().split("std.")[1]
            n_ctrls = instruction.num_controls()
            angle = rotation_angle(instruction)

            if op == "rx":
                op = "x"
                angle = None

            if op == "x":
                op = gates.X()

            if n_ctrls > 0:
                qb = []
                for u, pol in qubits:
                    if not pol:
                        qc.x(u)
                    qb.append(u)

                qc.mctrl(op, qb[0:-1], qb[-1], angle)

                for u, pol in qubits:
                    if not pol:
                        qc.x(u)
            else:
                qc.append(op, [qubits[0][0]])

        return qc
