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

from typing import Any, List, Tuple


class QGate:
    def __init__(self, name: str, n_qubits: int = 1):
        self.__name__ = name
        self.n_qubits = n_qubits

    def __repr__(self):
        return f"{self.__name__}"

    @classmethod
    def invert(cls):
        return cls

    def is_nop(self):
        return False


class NopGate(QGate):
    def __init__(self, name="nop"):
        super().__init__(name, 0)

    def is_nop(self):
        return True


class Barrier(NopGate):
    def __init__(self):
        super().__init__("_barrier")


class QControlledGate(QGate):
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


class CP(QControlledGate):
    def __init__(self):
        super().__init__(P(), 1)


class CCX(QControlledGate):
    def __init__(self):
        super().__init__(X(), 2)


Toffoli = CCX


class MCX(QControlledGate):
    def __init__(self, n_controls):
        super().__init__(X(), n_controls)


class MCtrl(QControlledGate):
    def __init__(self, gate, n_controls):
        super().__init__(gate, n_controls)


def apply(gate: QGate, qubits: List[int], param=None):
    if len(qubits) != gate.n_qubits:
        raise Exception(f"expected {gate.n_qubits} qubits ({len(qubits)} given)")
    return (
        gate,
        qubits,
        param,
    )


AppliedGate = Tuple[QGate, List[int], Any]
