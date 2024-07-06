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

import sys
from typing import Any, List, Literal, Tuple, TypeVar, Union

from sympy.logic.boolalg import Boolean, BooleanFalse, BooleanTrue, Not

if sys.version_info < (3, 11):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

if sys.version_info >= (3, 9):
    from builtins import type as Type
else:
    from typing import Type

TType: TypeAlias = Union[Type[bool], Type["Qtype"]]
TExp: TypeAlias = Tuple[TType, Boolean]

T = TypeVar("T")
TGExp = Tuple[T, Boolean]


class TypeErrorException(Exception):
    def __init__(self, got, excepted):
        super().__init__(f"Got '{got}' excepted '{excepted}'")


def bin_to_bool_list(b: str, bit_size=None) -> List[bool]:
    if b.startswith("0b"):
        b = b[2:]

    if bit_size is None:
        bit_size = len(b)

    s = list(
        map(
            lambda b: True if b == "1" else False,
            b[0:bit_size],
        )
    )
    return [False] * (bit_size - len(s)) + s


def bool_list_to_bin(b_lst: List[bool]) -> str:
    return "".join(map(lambda x: "1" if x else "0", b_lst))


class Qtype:
    BIT_SIZE = 0

    def __getitem__(self, i):
        """Return the i-nth bit value"""
        if i > self.BIT_SIZE:
            raise Exception("Unbound")

        return self.to_bin()[i] == "1"

    def to_bin(self) -> str:
        """Return the binary representation of the value"""
        bool_lst = self.to_bool()
        return "".join(map(lambda b: "1" if b else "0", bool_lst))

    def to_bool(self) -> List[bool]:
        """Return the bool representation of the value"""
        raise Exception("abstract to_bool")

    def to_amplitudes(self) -> List[float]:
        """Return amplitudes to initialize the current value on a quantum circuit"""
        raise Exception("abstract to_amplitudes")

    def export(self, mode: Literal["amplitudes", "binary"] = "binary"):
        if mode == "amplitudes":
            return self.to_amplitudes()
        elif mode == "binary":
            return self.to_bin()
        else:
            raise Exception(f"Mode {mode} not supported")

    @classmethod
    def from_bool(cls, v: List[bool]) -> "Qtype":
        """Return the Qtype object from a list of booleans"""
        raise Exception("abstract from_bool")

    @classmethod
    def from_bin(cls, v: str) -> "Qtype":
        """Return the Qtype object from a binary string"""
        bool_lst = list(map(lambda b: True if b == "1" else False, v))
        return cls.from_bool(bool_lst)

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        """Return true if the type is comparable with itself or
        with [other_type]"""
        raise Exception("abstract comparable")

    @classmethod
    def size(cls) -> int:
        """Return the size in bit"""
        return cls.BIT_SIZE

    @classmethod
    def const(cls, value: Any) -> TExp:
        """Return a list of bool representing the value"""
        raise Exception("abstract const")

    @classmethod
    def fill(cls, v: TExp) -> TExp:
        """Fill with leading false"""
        if len(v[1]) >= cls.BIT_SIZE:
            return v

        return (
            cls,
            v[1] + (cls.BIT_SIZE - len(v[1])) * [False],
        )

    @classmethod
    def crop(cls, v: TExp) -> TExp:
        """Crop to right size"""
        if len(v[1]) <= cls.BIT_SIZE:
            return v

        return (
            cls,
            v[1][: cls.BIT_SIZE],
        )

    @staticmethod
    def is_const(v: TExp) -> bool:
        """Return True if v is a constant"""
        for el in v[1]:
            if (
                not type(el) is bool
                and not isinstance(el, BooleanFalse)
                and not isinstance(el, BooleanTrue)
            ):
                return False
        return True

    # Comparators

    @staticmethod
    def eq(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract eq")

    @staticmethod
    def neq(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract neq")

    @staticmethod
    def gt(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract gt")

    @staticmethod
    def gte(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract gte")

    @staticmethod
    def lt(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract lt")

    @staticmethod
    def lte(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract lte")

    # Operations

    @staticmethod
    def bitwise_not(v: TExp) -> TExp:
        """Apply a bitwise not"""
        return (v[0], list(map(Not, v[1])))

    @staticmethod
    def shift_right(v: TExp, i: int = 1) -> TExp:
        """Apply a shift right"""
        if not issubclass(v[0], Qtype):
            raise TypeErrorException(v[0], Qtype)

        return v[0].fill((v[0], v[1][i:]))

    @staticmethod
    def shift_left(v: TExp, i: int = 1) -> TExp:
        """Apply a shift left"""
        if not issubclass(v[0], Qtype):
            raise TypeErrorException(v[0], Qtype)

        return v[0].crop((v[0], [False] * i + v[1]))

    @staticmethod
    def add(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract add")

    @staticmethod
    def sub(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract sub")

    @staticmethod
    def mul(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract mul")

    @staticmethod
    def mod(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract mod")

    @staticmethod
    def bitwise_xor(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract bitwise_xor")

    @staticmethod
    def bitwise_and(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract bitwise_and")

    @staticmethod
    def bitwise_or(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract bitwise_or")
