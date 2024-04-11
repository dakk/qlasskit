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

from typing import List, cast

from sympy import Symbol
from sympy.logic import And, Not, Or, false, true

from . import TypeErrorException, _eq, _neq
from .qint import QintImp
from .qtype import Qtype, TExp, bin_to_bool_list, bool_list_to_bin


class QfixedImp(float, Qtype):
    """Implementation of the Qfixed type
    A number i.f is encoded in a Qfixed2_4 as iiffff.
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
        # v = str(value).split('.')
        # self.value = int(v[0]) % self.BIT_SIZE_INTEGER + (float(f'0.{v[1]}')
        # if len(v) == 2 else 0)

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
        integer_part = bin_to_bool_list(
            bin(int(self.value))[::-1], self.BIT_SIZE_INTEGER
        )

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
            or issubclass(other_type, QintImp)
            or issubclass(other_type, QfixedImp)
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
        if not issubclass(v[0], QfixedImp):
            raise TypeErrorException(v[0], QfixedImp)

        return v[1][: v[0].BIT_SIZE_INTEGER]

    @staticmethod
    def fractional_part(v: TExp):
        """Return the fractional part of a TExp"""
        if not issubclass(v[0], QfixedImp):
            raise TypeErrorException(v[0], QfixedImp)

        return v[1][v[0].BIT_SIZE_INTEGER :]

    @staticmethod
    def _to_qint_repr(v: Qtype):
        if not issubclass(v[0], QfixedImp):
            raise TypeErrorException(v[0], QfixedImp)

        return v[0].fractional_part(v)[::-1] + v[0].integer_part(v)

    @staticmethod
    def _from_qint_repr(v: TExp):
        if not issubclass(v[0], QfixedImp):
            raise TypeErrorException(v[0], QfixedImp)

        return v[1][v[0].BIT_SIZE_FRACTIONAL :] + v[1][: v[0].BIT_SIZE_FRACTIONAL][::-1]

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
        if not issubclass(tleft[0], QfixedImp):
            raise TypeErrorException(tleft[0], QfixedImp)
        if not issubclass(tcomp[0], QfixedImp):
            raise TypeErrorException(tcomp[0], QfixedImp)

        tleft_e = cast(Qtype, tleft)
        tcomp_e = cast(Qtype, tcomp)

        tl_v = QfixedImp._to_qint_repr(tleft_e)
        tc_v = QfixedImp._to_qint_repr(tcomp_e)

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

    # Operations

    @classmethod
    def add(cls, tleft: TExp, tright: TExp) -> TExp:
        """Add two Qfixed"""
        if not issubclass(tright[0], QfixedImp):
            raise TypeErrorException(tright[0], QfixedImp)
        if not issubclass(tleft[0], QfixedImp):
            raise TypeErrorException(tleft[0], QfixedImp)

        tright_e = cast(Qtype, tright)
        tleft_e = cast(Qtype, tleft)

        if len(tleft_e[1]) > len(tright_e[1]):
            tright_e = tleft_e[0].fill(tright_e)

        elif len(tleft_e[1]) < len(tright_e[1]):
            tleft_e = tright_e[0].fill(tleft_e)

        tl_v = QfixedImp._to_qint_repr(tleft_e)
        tr_v = QfixedImp._to_qint_repr(tright_e)

        res = QintImp.add((tleft_e[0], tl_v), (tright_e[0], tr_v))

        return (tleft_e[0], QfixedImp._from_qint_repr((tleft_e[0], res[1])))

    @classmethod
    def sub(cls, tleft: TExp, tright: TExp) -> TExp:
        """Subtract two Qfixed"""
        if not issubclass(tleft[0], Qtype):
            raise TypeErrorException(tleft[0], Qtype)
        if not issubclass(tright[0], Qtype):
            raise TypeErrorException(tright[0], Qtype)

        an = cls.bitwise_not(cls.fill(tleft))
        su = cls.add(an, cls.fill(tright))
        return cls.bitwise_not(su)

    @classmethod
    def mul(cls, tleft: TExp, tright: TExp) -> TExp:  # noqa: C901
        if not issubclass(tright[0], Qtype):
            raise TypeErrorException(tright[0], Qtype)
        if not issubclass(tleft[0], Qtype):
            raise TypeErrorException(tleft[0], Qtype)

        a = len(list(filter(lambda b: b is bool, tleft[1])))
        b = len(list(filter(lambda b: b is bool, tright[1])))

        if a == 0 and issubclass(tleft[0], QintImp):
            tconst = tleft
            top = tright
        elif b == 0 and issubclass(tright[0], QintImp):
            top = tleft
            tconst = tright
        else:
            raise Exception(
                "Qfixed mul works only between a Qfixed and an integer constant"
            )

        v_const = int(bool_list_to_bin(tconst[1])[::-1], 2)

        if v_const == 0:
            return cls.const(0.0)

        v = top
        for i in range(v_const - 1):
            v = cls.add(v, top)

        return v


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


class Qfixed3_3(QfixedImp):
    BIT_SIZE = 6
    BIT_SIZE_INTEGER = 3
    BIT_SIZE_FRACTIONAL = 3


class Qfixed3_4(QfixedImp):
    BIT_SIZE = 7
    BIT_SIZE_INTEGER = 3
    BIT_SIZE_FRACTIONAL = 4


class Qfixed3_6(QfixedImp):
    BIT_SIZE = 9
    BIT_SIZE_INTEGER = 3
    BIT_SIZE_FRACTIONAL = 6


class Qfixed4_4(QfixedImp):
    BIT_SIZE = 8
    BIT_SIZE_INTEGER = 4
    BIT_SIZE_FRACTIONAL = 4


class Qfixed4_6(QfixedImp):
    BIT_SIZE = 10
    BIT_SIZE_INTEGER = 4
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
    Qfixed3_3,
    Qfixed3_4,
    Qfixed3_6,
    Qfixed4_4,
    Qfixed4_6,
]

# class _GetQfixedTypeInner:
#     def __init__(self, base):
#         self.base = base

#     def __getitem__(self, index):
#         return eval(f"Qfixed{self.base}_{index}")

# class _GetQfixedType:
#     @property
#     def __name__(self):
#         return 'Qfixed' # I'm not sure this is correct

#     def __getitem__(self, index):
#         return _GetQfixedTypeInner(index)


class QfixedMeta(type):
    def __getitem__(cls, params):
        if isinstance(params, tuple) and len(params) == 2:
            i, f = params
            if isinstance(i, int) and isinstance(f, int) and i >= 0 and f >= 0:
                return f"Qfixed{i}_{f}"

    # def __new__(cls, name, bases, dct):
    #     return _GetQfixedType()


class Qfixed(metaclass=QfixedMeta):
    @staticmethod
    def type_for_size(s: int):
        for det_type in QFIXED_TYPES:
            if det_type.BIT_SIZE_INTEGER == s:
                return det_type
