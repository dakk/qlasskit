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
from __future__ import annotations

from typing import Any, List, Tuple


class QGate:
    __name__: str
    n_qubits: int

    def __init__(self, name: str, n_qubits: int = 1):
        self.__name__ = name
        self.n_qubits = n_qubits

    @property
    def name(self) -> str:
        return self.__name__

    def __repr__(self) -> str:
        return f"{self.__name__}"

    @classmethod
    def invert(cls) -> type[QGate]:
        return cls

    def is_nop(self) -> bool:
        return False


class NopGate(QGate):
    def __init__(self, name: str = "nop"):
        super().__init__(name, 0)

    def is_nop(self) -> bool:
        return True


class Barrier(NopGate):
    def __init__(self):
        super().__init__("_barrier")


class QControlledGate(QGate):
    n_controls: int
    gate: QGate

    def __init__(self, gate: QGate, n_controls: int):
        super().__init__(("C" * n_controls) + gate.__name__, n_controls + gate.n_qubits)
        self.n_controls = n_controls
        self.gate = gate


class I(QGate):  # noqa: E742
    def __init__(self):
        super().__init__("I", 1)


class X(QGate):
    def __init__(self):
        super().__init__("X")


class Y(QGate):
    def __init__(self):
        super().__init__("Y")


class S(QGate):
    def __init__(self):
        super().__init__("S")


class T(QGate):
    def __init__(self):
        super().__init__("T")


class H(QGate):
    def __init__(self):
        super().__init__("H")


class Z(QGate):
    def __init__(self):
        super().__init__("Z")


class P(QGate):
    def __init__(self):
        super().__init__("P")


class Swap(QGate):
    def __init__(self):
        super().__init__("SWAP", 2)


class CX(QControlledGate):
    def __init__(self):
        super().__init__(X(), 1)


class CZ(QControlledGate):
    def __init__(self):
        super().__init__(Z(), 1)


class CP(QControlledGate):
    def __init__(self):
        super().__init__(P(), 1)


class CCX(QControlledGate):
    def __init__(self):
        super().__init__(X(), 2)


Toffoli = CCX


class MCX(QControlledGate):
    def __init__(self, n_controls: int):
        super().__init__(X(), n_controls)


class MCtrl(QControlledGate):
    def __init__(self, gate: QGate, n_controls: int):
        super().__init__(gate, n_controls)


AppliedGate = Tuple[QGate, List[int], Any]


def apply(gate: QGate, qubits: List[int], param=None) -> AppliedGate:
    if len(qubits) != gate.n_qubits:
        raise Exception(f"expected {gate.n_qubits} qubits ({len(qubits)} given)")
    return (
        gate,
        qubits,
        param,
    )
