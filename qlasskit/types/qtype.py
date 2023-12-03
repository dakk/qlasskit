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

import sys
from typing import Any, List, Literal, Tuple

from sympy.logic.boolalg import Boolean, Not

if sys.version_info < (3, 11):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

TType: TypeAlias = object
TExp: TypeAlias = Tuple[TType, Boolean]


class Qtype:
    BIT_SIZE = 0

    def __getitem__(self, i):
        """Return the i-nth bit value"""
        if i > self.BIT_SIZE:
            raise Exception("Unbound")

        return self.to_bin()[i] == "1"

    def to_bin(self) -> str:
        """Return the binary representation of the value"""
        raise Exception("abstract")

    def to_amplitudes(self) -> List[float]:
        """Return amplitudes to initialize the current value on a quantum circuit"""
        raise Exception("abstract")

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
        raise Exception("abstract")

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        """Return true if the type is comparable with itself or
        with [other_type]"""
        raise Exception("abstract")

    @classmethod
    def size(cls) -> int:
        """Return the size in bit"""
        return cls.BIT_SIZE

    @classmethod
    def const(cls, value: Any) -> TExp:
        """Return a list of bool representing the value"""
        raise Exception("abstract")

    @staticmethod
    def fill(v: TExp) -> TExp:
        """Fill with leading false"""
        raise Exception("abstract")

    @staticmethod
    def crop(v: TExp) -> TExp:
        """Crop to right size"""
        raise Exception("abstract")

    # Comparators

    @staticmethod
    def eq(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def neq(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def gt(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def gte(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def lt(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def lte(tleft: TExp, tcomp: TExp) -> TExp:
        raise Exception("abstract")

    # Operations

    @staticmethod
    def bitwise_not(v: TExp) -> TExp:
        """Apply a bitwise not"""
        return (v[0], list(map(Not, v[1])))

    @staticmethod
    def shift_right(v: TExp, i: int = 1) -> TExp:
        """Apply a shift right"""
        return (v[0], v[1][i:])

    @staticmethod
    def shift_left(v: TExp, i: int = 1) -> TExp:
        """Apply a shift left"""
        return (v[0], [False] * i + v[1])

    @staticmethod
    def add(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def sub(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def mul(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def mod(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def bitwise_xor(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def bitwise_and(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")

    @staticmethod
    def bitwise_or(tleft: TExp, tright: TExp) -> TExp:
        raise Exception("abstract")
