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

from typing import List, Tuple

from sympy import Symbol
from sympy.logic import And, Not, Or, false, true
from sympy.logic.boolalg import Boolean
from typing_extensions import TypeAlias

# from .ast2logic.t_expression import TType

TType: TypeAlias = object
TExp: TypeAlias = Tuple[TType, Boolean]


def xnor(a, b):
    return Or(And(a, b), And(Not(a), Not(b)))


class Arg:
    def __init__(self, name: str, ttype: object, bitvec: List[str]):
        self.name = name
        self.ttype = ttype
        self.bitvec = bitvec

    def __repr__(self):
        return f"{self.name} - {self.ttype} - {', '.join(self.bitvec)}"

    def __len__(self) -> int:
        return len(self.bitvec)

    def to_exp(self) -> List[Symbol]:
        if len(self) > 1:
            return list(map(Symbol, self.bitvec))
        return Symbol(self.bitvec[0])


Args = List[Arg]
BoolExpList = List[Tuple[Symbol, Boolean]]
LogicFun = Tuple[str, Args, int, BoolExpList]


class Qtype:
    BIT_SIZE = 0


class Qint(int, Qtype):
    BIT_SIZE = 8

    def __init__(self, value):
        super().__init__()
        self.value = value

    @staticmethod
    def const(v: int) -> List[bool]:
        """Return the list of bool representing an int"""
        return list(map(lambda c: True if c == "1" else False, bin(v)[2:]))

    @staticmethod
    def fill(v: Tuple[TType, List[bool]]) -> Tuple[TType, List[bool]]:
        """Fill a Qint to reach its bit_size"""
        if len(v[1]) < v[0].BIT_SIZE:  # type: ignore
            v = (
                v[0],
                [False] * (v[0].BIT_SIZE - len(v[1])) + v[1],  # type: ignore
            )
        return v

    @staticmethod
    def eq(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for equality"""
        ex = true
        for x in zip(tleft[1], tcomp[1]):
            ex = And(ex, xnor(x[0], x[1]))

        if len(tleft[1]) > len(tcomp[1]):
            for x in tleft[1][len(tcomp[1]) :]:
                ex = And(ex, Not(x))

        if len(tleft[1]) < len(tcomp[1]):
            for x in tcomp[1][len(tleft[1]) :]:
                ex = And(ex, Not(x))

        return (bool, ex)

    @staticmethod
    def not_eq(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for inequality"""
        return (bool, Not(Qint.eq(tleft, tcomp)[1]))

    @staticmethod
    def gt(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for greater than"""
        ex = false

        for x in list(zip(tleft[1], tcomp[1]))[::-1]:
            ex = Or(ex, And(Not(ex), And(Not(x[1]), x[0])))

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
