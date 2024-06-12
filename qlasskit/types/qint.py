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

from typing import List, cast

from sympy import Symbol
from sympy.logic import And, Not, Or, Xor, false, true

from . import TypeErrorException, _eq, _full_adder, _neq
from .qtype import Qtype, TExp, TType, bin_to_bool_list, bool_list_to_bin


class QintImp(int, Qtype):
    BIT_SIZE = 8

    def __init__(self, value):
        super().__init__()
        self.value = value % 2**self.BIT_SIZE

    def __add__(self, b):
        return (self.value + b) % 2**self.BIT_SIZE

    def __sub__(self, b):
        return (self.value - b) % 2**self.BIT_SIZE

    @classmethod
    def from_bool(cls, v: List[bool]):
        return cls(int(bool_list_to_bin(v[::-1]), 2))

    def to_bool(self) -> List[bool]:
        return bin_to_bool_list(bin(self.value), self.BIT_SIZE)[::-1]

    def to_amplitudes(self) -> List[float]:
        ampl = [0.0] * 2**self.BIT_SIZE
        ampl[self.value] = 1
        return ampl

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        """Return true if the type is comparable with itself or
        with [other_type]"""
        if not other_type or issubclass(other_type, QintImp):
            return True
        return False

    @classmethod
    def const(cls, v: int) -> TExp:
        """Return the list of bool representing an int"""
        cval = list(map(lambda c: True if c == "1" else False, bin(v)[2:]))
        return cls.fill((cls, cval[::-1]))

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
        return (
            bool,
            And(Not(QintImp.gt(tleft, tcomp)[1]), Not(QintImp.eq(tleft, tcomp)[1])),
        )

    @staticmethod
    def lte(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for lower than - equal"""
        return (bool, Not(QintImp.gt(tleft, tcomp)[1]))

    @staticmethod
    def gte(tleft: TExp, tcomp: TExp) -> TExp:
        """Compare two Qint for greater than - equal"""
        return (bool, Not(QintImp.lt(tleft, tcomp)[1]))

    # Operations

    @classmethod
    def add(cls, tleft: TExp, tright: TExp) -> TExp:
        """Add two Qint"""
        if not issubclass(tleft[0], Qtype):
            raise TypeErrorException(tleft[0], Qtype)
        if not issubclass(tright[0], Qtype):
            raise TypeErrorException(tright[0], Qtype)

        tright_e = cast(Qtype, tright)
        tleft_e = cast(Qtype, tleft)

        if len(tleft_e[1]) > len(tright_e[1]):
            tright_e = tleft_e[0].fill(tright_e)

        elif len(tleft_e[1]) < len(tright_e[1]):
            tleft_e = tright_e[0].fill(tleft_e)

        carry = False
        sums = []
        for x in zip(tleft_e[1], tright_e[1]):
            carry, sum = _full_adder(carry, x[0], x[1])
            sums.append(sum)

        return (cls if cls.BIT_SIZE > tleft_e[0].BIT_SIZE else tleft_e[0], sums)

    @staticmethod
    def mul_even_const(t_num: TExp, const: int, result_type: Qtype) -> TExp:
        """Multiply by an even const using shift and add
        (x << 3) + (x << 1) # Here 10*x is computed as x*2^3 + x*2
        """

        # Multiply t_num by the nearest n | 2**n < t_const
        n = 1
        while 2**n <= const:
            n += 1
        if 2**n > const:
            n -= 1

        result_ttype = cast(TType, result_type)

        t_num_r = result_type.shift_left((result_ttype, t_num[1]), n)

        # Shift t_const by t_const - 2**n
        r = const - 2**n
        if r > 0:
            # Add the shift result to t_num
            res = result_type.add(
                (result_ttype, t_num_r[1]),
                result_type.shift_left((result_ttype, t_num[1]), int(r / 2)),
            )
        else:
            res = (result_ttype, t_num_r[1])

        return res

    @classmethod
    def mul(cls, tleft_: TExp, tright_: TExp) -> TExp:  # noqa: C901
        if not issubclass(tleft_[0], Qtype):
            raise TypeErrorException(tleft_[0], Qtype)
        if not issubclass(tright_[0], Qtype):
            raise TypeErrorException(tright_[0], Qtype)

        def __mul_sizing(n, m):
            if (n + m) <= 2:
                return Qint2
            elif (n + m) > 2 and (n + m) <= 4:
                return Qint4
            elif (n + m) > 4 and (n + m) <= 6:
                return Qint6
            elif (n + m) > 6 and (n + m) <= 8:
                return Qint8
            elif (n + m) > 8 and (n + m) <= 12:
                return Qint12
            elif (n + m) > 12 and (n + m) <= 16:
                return Qint16
            elif (n + m) > 16:
                return Qint16
            else:
                raise Exception(f"Mul result size is too big ({n+m})")

        # Fill constants so explicit typecast is not needed
        if cls.is_const(tleft_):
            tleft = tright_[0].fill(tleft_)
        else:
            tleft = tleft_

        if cls.is_const(tright_):
            tright = tleft_[0].fill(tright_)
        else:
            tright = tright_

        n = len(tleft[1])
        m = len(tright[1])

        # Ensure same size operands by padding the smaller one
        if n != m:
            if n > m:
                tright = tleft_[0].fill(tright)
                m = n
            else:
                tleft = tright_[0].fill(tleft)
                n = m

        # If one operand is an even constant, use mul_even_const
        if cls.is_const(tleft) or cls.is_const(tright):
            t_num = tleft if cls.is_const(tright) else tright
            t_const = tleft if cls.is_const(tleft) else tright
            const = cast(int, cast(Qtype, t_const[0]).from_bool(t_const[1]))

            if const % 2 == 0:
                t = __mul_sizing(n, m)
                res = cls.mul_even_const(t_num, const, t)
                return t.crop(t.fill(res))

        # if n != m:
        #     raise Exception(f"Mul works only on same size Qint: {n} != {m}")

        product = [False] * (n + m)

        for i in range(n):
            carry = False
            for j in range(m):
                partial_product = And(tleft[1][i], tright[1][j])

                if i + j < n + m - 1:
                    carry, sum_ = _full_adder(carry, partial_product, product[i + j])
                else:
                    sum_ = Xor(carry, partial_product)

                product[i + j] = sum_

            if i + m < n + m:
                product[i + m] = carry

        t = __mul_sizing(n, m)
        return t.crop(t.fill((t, product)))

    @classmethod
    def sub(cls, tleft: TExp, tright: TExp) -> TExp:
        """Subtract two Qint"""
        an = cls.bitwise_not(cls.fill(tleft))
        su = cls.add(an, cls.fill(tright))
        return cls.bitwise_not(su)

    @classmethod
    def mod(cls, tleft: TExp, tright: TExp) -> TExp:  # noqa: C901
        # x mod y = x & (y - 1)
        if not issubclass(tleft[0], Qtype):
            raise TypeErrorException(tleft[0], Qtype)
        if not issubclass(tright[0], Qtype):
            raise TypeErrorException(tright[0], Qtype)

        tval = tright[0].sub(tright, tright[0].const(1))
        return tleft[0].bitwise_and(tleft, tval)

    @classmethod
    def bitwise_generic(cls, op, tleft: TExp, tright: TExp) -> TExp:
        """Bitwise generic"""
        if not issubclass(tleft[0], Qtype):
            raise TypeErrorException(tleft[0], Qtype)
        if not issubclass(tright[0], Qtype):
            raise TypeErrorException(tright[0], Qtype)

        tright_e = cast(Qtype, tright)
        tleft_e = cast(Qtype, tleft)

        if len(tleft_e[1]) > len(tright_e[1]):
            tright_e = tleft_e[0].fill(tright_e)

        elif len(tleft_e[1]) < len(tright_e[1]):
            tleft_e = tright_e[0].fill(tleft_e)

        newl = [op(a, b) for (a, b) in zip(tleft_e[1], tright_e[1])]
        return (tright_e[0], newl)

    @classmethod
    def bitwise_xor(cls, tleft: TExp, tright: TExp) -> TExp:
        return cls.bitwise_generic(Xor, tleft, tright)

    @classmethod
    def bitwise_and(cls, tleft: TExp, tright: TExp) -> TExp:
        return cls.bitwise_generic(And, tleft, tright)

    @classmethod
    def bitwise_or(cls, tleft: TExp, tright: TExp) -> TExp:
        return cls.bitwise_generic(Or, tleft, tright)


class Qint2(QintImp):
    BIT_SIZE = 2


class Qint3(QintImp):
    BIT_SIZE = 3


class Qint4(QintImp):
    BIT_SIZE = 4


class Qint5(QintImp):
    BIT_SIZE = 5


class Qint6(QintImp):
    BIT_SIZE = 6


class Qint7(QintImp):
    BIT_SIZE = 7


class Qint8(QintImp):
    BIT_SIZE = 8


class Qint12(QintImp):
    BIT_SIZE = 12


class Qint16(QintImp):
    BIT_SIZE = 16


QINT_TYPES = [Qint2, Qint3, Qint4, Qint5, Qint6, Qint7, Qint8, Qint12, Qint16]

# class _GetQintType:
#     @property
#     def __name__(self):
#         return 'Qint' # I'm not sure this is correct

#     def __getitem__(self, index):
#         return eval(f"Qint{index}")


class QintMeta(type):
    def __getitem__(cls, params):
        if isinstance(params, tuple) and len(params) == 1:
            i = params
            if isinstance(i, int) and i >= 2:
                return f"Qint{i}"

    # def __new__(cls, name, bases, dct):
    #     return _GetQintType()


class Qint(metaclass=QintMeta):
    @staticmethod
    def type_for_size(s: int):
        for det_type in QINT_TYPES:
            if det_type.BIT_SIZE == s:
                return det_type
