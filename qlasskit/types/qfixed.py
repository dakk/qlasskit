# Copyright 2024 Davide Gessa

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
from math import frexp, ldexp

from sympy.logic import And, Or, false, true

from . import _eq, _neq
from .qint import Qint
from .qtype import Qtype, TExp


class QfixedImp(float, Qtype):
    """Implementation of the Qfixed type
    A number i.f is encoded in a Qfixed_2_4 as iiffff in little endian
    """

    BIT_SIZE = 4
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FRACTIONAL = 2

    def __init__(self, value: float):
        super().__init__()
        self.value = value

    @classmethod
    def from_bool(cls, v: List[bool]):
        # Dividi la lista in parte intera e frazionaria.
        integer_part = v[:cls.BIT_SIZE_INTEGER]
        fractional_part = v[cls.BIT_SIZE_INTEGER:]

        # Converti la parte intera in un numero intero.
        integer_value = int("".join(
            map(lambda x: "1" if x else "0", v[0 : cls.BIT_SIZE_INTEGER])
        )[::-1], 2)

        # Converti la parte frazionaria in un numero decimale.
        fractional_value = 0
        for i, bit in enumerate(fractional_part):
            if bit:
                fractional_value += 2**(-(i + 1))

        # Combina la parte intera e frazionaria in un float.
        return integer_value + fractional_value


    def to_bin(self) -> str:
        # Ottieni l'esponente e la mantissa del float.
        exponent, mantissa = frexp(self.value)

        # Converti l'esponente in binario.
        exponent_bin = bin(exponent + (2**self.BIT_SIZE_INTEGER - 1))[2:].zfill(self.BIT_SIZE_INTEGER)

        # Converti la mantissa in binario.
        mantissa_bin = "1"
        for i in range(self.BIT_SIZE_FRACTIONAL):
            mantissa *= 2
            mantissa_bin += str(int(mantissa))
            mantissa -= int(mantissa)

        # Combina l'esponente e la mantissa in una stringa binaria.
        return exponent_bin + mantissa_bin[:self.BIT_SIZE_FRACTIONAL]

    def to_amplitudes(self) -> List[float]:
        ampl = [0.0] * 2**self.BIT_SIZE
        ampl[int(self.to_bin(), 2)] = 1
        return ampl

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        return (
            other_type == cls
            or issubclass(other_type, Qint)
            or issubclass(other_type, QfixedImp)
        )

    @classmethod
    def fill(cls, v: TExp) -> TExp:
        if len(v[1]) < cls.BIT_SIZE:  # type: ignore
            v = (
                cls,
                v[1] + (cls.BIT_SIZE - len(v[1])) * [False],  # type: ignore
            )
        return v

    @classmethod
    def const(cls, v: float) -> TExp:
        """Return the list of bool representing a fixed"""
        v = cls(v).to_bin()
        return (cls, list(map(lambda c: True if c == "1" else False, v)))

    # Comparators

    @staticmethod
    def eq(tleft: TExp, tcomp: TExp) -> TExp:
        ex = true
        for x in zip(tleft[1], tcomp[1]):
            ex = And(ex, _eq(x[0], x[1]))

        return (bool, ex)

    @staticmethod
    def neq(tleft: TExp, tcomp: TExp) -> TExp:
        ex = false
        for x in zip(tleft[1], tcomp[1]):
            ex = Or(ex, _neq(x[0], x[1]))

        return (bool, ex)


class Qfixed1_2(QfixedImp):
    BIT_SIZE = 3
    BIT_SIZE_INTEGER = 1
    BIT_SIZE_FRACTIONAL = 2


class Qfixed1_3(QfixedImp):
    BIT_SIZE = 4
    BIT_SIZE_INTEGER = 1
    BIT_SIZE_FRACTIONAL = 3


class Qfixed1_4(QfixedImp):
    BIT_SIZE = 5
    BIT_SIZE_INTEGER = 1
    BIT_SIZE_FRACTIONAL = 4


class Qfixed1_6(QfixedImp):
    BIT_SIZE = 7
    BIT_SIZE_INTEGER = 1
    BIT_SIZE_FRACTIONAL = 6


class Qfixed2_2(QfixedImp):
    BIT_SIZE = 4
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FRACTIONAL = 2


class Qfixed2_3(QfixedImp):
    BIT_SIZE = 5
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FRACTIONAL = 3


class Qfixed2_4(QfixedImp):
    BIT_SIZE = 6
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FRACTIONAL = 4


class Qfixed2_6(QfixedImp):
    BIT_SIZE = 8
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FRACTIONAL = 6


QFIXED_TYPES = [
    Qfixed1_2,
    Qfixed1_3,
    Qfixed1_4,
    Qfixed1_6,
    Qfixed2_2,
    Qfixed2_3,
    Qfixed2_4,
    Qfixed2_6,
]


class QfixedMeta(type):
    def __getitem__(cls, params):
        if isinstance(params, tuple) and len(params) == 2:
            i, f = params
            if isinstance(i, int) and isinstance(f, int) and i >= 0 and f >= 0:
                return f"Qfixed{i}_{f}"  # TODO: transform to type


class Qfixed(metaclass=QfixedMeta):
    pass
