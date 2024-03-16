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

from sympy import Symbol
from sympy.logic import And, Not, Or, false, true

from . import _eq, _neq
from .qint import Qint
from .qtype import Qtype, TExp, bin_to_bool_list, bool_list_to_bin


class QfixedImp(float, Qtype):
    """Implementation of the Qfixed type
    A number i.f is encoded in a Qfixed_2_4 as iiffff.
    The interger part is in little endian like Qint
    Fractional part is obtained as binary fractions, by multiplying for
    2 and getting the integer part at each step.

    0.1:
    -> 0.1 x 2 = 0.2 (0)
    -> 0.2 x 2 = 0.4 (0)
    -> 0.4 x 2 = 0.8 (0)
    -> 0.8 x 2 = 1.6 (1)
    -> 0.6 x 2 = 1.2 (1)
    -> and so on

    so we get 0.00011 (this is an approximation)

    if we want to get again the number in deciaml we multiply each binary
    position by 2 ** -i.
    """

    BIT_SIZE = 4
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FRACTIONAL = 2

    def __init__(self, value: float):
        super().__init__()
        self.value = value

    @classmethod
    def from_bool(cls, v: List[bool]):
        integer_part = v[: cls.BIT_SIZE_INTEGER]
        fractional_part = v[cls.BIT_SIZE_INTEGER :]

        # Integer part
        integer_value = int(
            bool_list_to_bin(integer_part[::-1]),
            2,
        )

        # Fractional part
        fractional_value = 0
        for i, bit in enumerate(fractional_part):
            if bit:
                fractional_value += 2 ** (-(i + 1))

        return cls(integer_value + fractional_value)

    def to_bool(self) -> List[bool]:
        integer_part = bin_to_bool_list(bin(int(self.value)), self.BIT_SIZE_INTEGER)[
            ::-1
        ]

        fractional_part = []
        c_val = self.value
        for i in range(self.BIT_SIZE_FRACTIONAL):
            c_val = c_val % 1
            c_val *= 2
            fractional_part += [int(c_val) == 1]

        return integer_part + fractional_part

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
        if len(v[1]) >= cls.BIT_SIZE:  # type: ignore
            return v

        return (
            cls,
            v[1] + (cls.BIT_SIZE - len(v[1])) * [False],  # type: ignore
        )

    @classmethod
    def const(cls, v: float) -> TExp:
        """Return the list of bool representing a fixed"""
        v_bool = cls(v).to_bool()
        return (cls, v_bool)

    # Comparators

    @staticmethod
    def integer_part(v: TExp):
        """Return the integer part of a TExp"""
        return v[1][: v[0].BIT_SIZE_INTEGER]  # type: ignore

    @staticmethod
    def fractional_part(v: TExp):
        """Return the fractional part of a TExp"""
        return v[1][v[0].BIT_SIZE_INTEGER :]  # type: ignore

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

    @staticmethod
    def gt(tleft: TExp, tcomp: TExp) -> TExp:
        tl_v = tleft[0].fractional_part(tleft)[::-1] + tleft[0].integer_part(tleft)  # type: ignore
        tc_v = tcomp[0].fractional_part(tcomp)[::-1] + tcomp[0].integer_part(tcomp)  # type: ignore

        prev: List[Symbol] = []

        for a, b in list(zip(tl_v, tc_v))[::-1]:
            if len(prev) == 0:
                ex = And(a, Not(b))
            else:
                ex = Or(ex, And(*(prev + [a, Not(b)])))

            prev.append(_eq(a, b))

        if len(tl_v) > len(tc_v):
            for x in tl_v[len(tc_v) :]:
                ex = Or(ex, x)

        if len(tl_v) < len(tc_v):
            for x in tc_v[len(tl_v) :]:
                ex = Or(ex, x)

        return (bool, ex)

    @staticmethod
    def lt(tleft: TExp, tcomp: TExp) -> TExp:
        return (
            bool,
            And(Not(QfixedImp.gt(tleft, tcomp)[1]), Not(QfixedImp.eq(tleft, tcomp)[1])),
        )

    @staticmethod
    def lte(tleft: TExp, tcomp: TExp) -> TExp:
        return (bool, Not(QfixedImp.gt(tleft, tcomp)[1]))

    @staticmethod
    def gte(tleft: TExp, tcomp: TExp) -> TExp:
        return (bool, Not(QfixedImp.lt(tleft, tcomp)[1]))


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
