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

from typing import List


class QGate:
    def __init__(self, name: str, n_qubits: int = 1):
        self.__name__ = name
        self.n_qubits = n_qubits

    @classmethod
    def invert(cls):
        return cls


class QControlledGate(QGate):
    def __init__(self, gate: QGate, n_controls: int):
        super().__init__("C" + gate.__name__)
        self.n_controls = n_controls


class X(QGate):
    def __init__(self):
        super().__init__("X")


class H(QGate):
    def __init__(self):
        super().__init__("H")


class Z(QGate):
    def __init__(self):
        super().__init__("Z")


def CX(QControlledGate):
    def __init__(self):
        super().__init__(X(), 1)


def CCX(QControlledGate):
    def __init__(self):
        super().__init__(X(), 2)


Toffoli = CCX


def MCX(QControlledGate):
    def __init__(self, n_controls):
        super().__init__(X(), n_controls)


def apply(gate: QGate, qubits: List[int], param=None):
    pass


# qc.append(CX(), [0, 1])
# qc += apply(CX(), [0, 1])
# qc += another_circ
