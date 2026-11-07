# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Literal

from sympy.physics.quantum.gate import CNOT, SWAP, CGate, H, X, XGate
from sympy.physics.quantum.qubit import Qubit

from . import gates
from .exporter import QCircuitExporter

# def cp(theta, q0, q1):
#     return CGate((q0,), Z(q1)**(theta))


def mcx(w):
    return CGate(tuple(w[0:-1]), XGate(w[-1]))


def toffoli(q0, q1, q2):
    return CGate((q0, q1), XGate(q2))


class SympyExporter(QCircuitExporter):
    def export(self, _selfqc, mode: Literal["circuit", "gate"]):  # noqa: C901
        qstate = Qubit("0" * _selfqc.num_qubits) if mode == "circuit" else None

        for g, w, p in _selfqc.gates:
            g_name = g.__class__.__name__
            ga = None
            if isinstance(g, gates.X):
                ga = X(w[0])
            elif isinstance(g, gates.H):
                ga = H(w[0])
            elif isinstance(g, gates.CX):
                ga = CNOT(w[0], w[1])
            # elif isinstance(g, gates.CP):
            #     ga = cp(p, w[0], w[1])
            elif isinstance(g, gates.Swap):
                ga = SWAP(w[0], w[1])
            elif isinstance(g, gates.CCX) or isinstance(g, gates.MCX):
                ga = mcx(w)
            elif isinstance(g, gates.Barrier) and mode != "gate":
                pass
            elif issubclass(g.__class__, gates.NopGate):
                pass
            else:
                raise Exception(f"Gate not handled for sympy exporter: {g_name}")

            if ga and qstate:
                qstate = ga * qstate
            elif ga:
                qstate = ga

        return qstate
