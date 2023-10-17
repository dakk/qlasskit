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

from sympy import Symbol
from sympy.logic import And, Not, Or, false, true

from . import _eq, _neq
from .qtype import Qtype, TExp


class Qint(int, Qtype):
    BIT_SIZE = 8

    def __init__(self, value):
        super().__init__()
        self.value = value

    @classmethod
    def from_bool(cls, v: List[bool]):
        return cls(int("".join(map(lambda x: "1" if x else "0", v[::-1])), 2))

    def to_bin(self) -> str:
        s = bin(self.value)[2:][0 : self.BIT_SIZE]
        return ("0" * (self.BIT_SIZE - len(s)) + s)[::-1]

    def to_amplitudes(self) -> List[float]:
        ampl = [0.0] * 2**self.BIT_SIZE
        ampl[self.value] = 1
        return ampl

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        """Return true if the type is comparable with itself or
        with [other_type]"""
        if not other_type or issubclass(other_type, Qint):
            return True
        return False

    @classmethod
    def const(cls, v: int) -> TExp:
        """Return the list of bool representing an int"""
        return cls.fill(
            (cls, list(map(lambda c: True if c == "1" else False, bin(v)[2:]))[::-1])
        )

    @staticmethod
    def fill(v: TExp) -> TExp:
        """Fill a Qint to reach its bit_size"""
        if len(v[1]) < v[0].BIT_SIZE:  # type: ignore
            v = (
                v[0],
                (v[0].BIT_SIZE - len(v[1])) * v[1] + [False],  # type: ignore
            )
        return v

    # Comparators

    @staticmethod
    def eq(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for equality"""
        ex = true
        for x in zip(tleft[1], tcomp[1]):
            ex = And(ex, _eq(x[0], x[1]))

        if len(tleft[1]) > len(tcomp[1]):
            for x in tleft[1][len(tcomp[1]) :]:
                ex = And(ex, Not(x))

        if len(tleft[1]) < len(tcomp[1]):
            for x in tcomp[1][len(tleft[1]) :]:
                ex = And(ex, Not(x))

        return (bool, ex)

    @staticmethod
    def neq(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for inequality"""
        ex = false
        for x in zip(tleft[1], tcomp[1]):
            ex = Or(ex, _neq(x[0], x[1]))

        if len(tleft[1]) > len(tcomp[1]):
            for x in tleft[1][len(tcomp[1]) :]:
                ex = Or(ex, x)

        if len(tleft[1]) < len(tcomp[1]):
            for x in tcomp[1][len(tleft[1]) :]:
                ex = Or(ex, x)

        return (bool, ex)

    @staticmethod
    def gt(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for greater than"""
        prev: List[Symbol] = []

        for a, b in list(zip(tleft[1], tcomp[1]))[::-1]:
            if len(prev) == 0:
                ex = And(a, Not(b))
            else:
                ex = Or(ex, And(*(prev + [a, Not(b)])))

            prev.append(_eq(a, b))

        if len(tleft[1]) > len(tcomp[1]):
            for x in tleft[1][len(tcomp[1]) :]:
                ex = Or(ex, x)

        if len(tleft[1]) < len(tcomp[1]):
            for x in tcomp[1][len(tleft[1]) :]:
                ex = Or(ex, x)

        return (bool, ex)

    @staticmethod
    def lt(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for lower than"""
        return (bool, And(Not(Qint.gt(tleft, tcomp)[1]), Not(Qint.eq(tleft, tcomp)[1])))

    @staticmethod
    def lte(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for lower than - equal"""
        return (bool, Not(Qint.gt(tleft, tcomp)[1]))

    @staticmethod
    def gte(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for greater than - equal"""
        return (bool, Not(Qint.lt(tleft, tcomp)[1]))

    # @staticmethod
    # def add(tleft: TExp, tright: TExp) -> TExp:
    #     """Add two Qint"""


class Qint2(Qint):
    BIT_SIZE = 2


class Qint4(Qint):
    BIT_SIZE = 4


class Qint8(Qint):
    BIT_SIZE = 8


class Qint12(Qint):
    BIT_SIZE = 12


class Qint16(Qint):
    BIT_SIZE = 16


# class Qlist
# class Qfixed
