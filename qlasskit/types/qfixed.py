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

from sympy.logic import And, Or, false, true

from . import _eq, _neq
from .qint import Qint
from .qtype import Qtype, TExp


class QfixedImp(float, Qtype):
    BIT_SIZE = 4
    BIT_SIZE_INTEGER = 2
    BIT_SIZE_FACTORIAL = 2

    def __init__(self, value: float):
        super().__init__()
        self.value = value

    @classmethod
    def from_bool(cls, v: List[bool]):
        i = "".join(
            map(lambda x: "1" if x else "0", v[::-1][0 : cls.BIT_SIZE_INTEGER])
        )[::-1]
        f = "".join(
            map(
                lambda x: "1" if x else "0",
                v[::-1][cls.BIT_SIZE_INTEGER : cls.BIT_SIZE_FACTORIAL],
            )
        )[::-1]
        print(int(i,2),int(f,2))
        return cls(float(f"{int(i,2)}.{int(f,2)}"))

    def to_bin(self) -> str:
        v_s = str(self.value).split(".")
        i = bin(int(v_s[0]) % 2**self.BIT_SIZE_INTEGER)[2:][0 : self.BIT_SIZE_INTEGER]
        f = bin(int(v_s[1]) % 2**self.BIT_SIZE_FACTORIAL)[2:][
            0 : self.BIT_SIZE_FACTORIAL
        ]
        v = ("0" * (self.BIT_SIZE_INTEGER - len(i)) + i) + (
            f + "0" * (self.BIT_SIZE_FACTORIAL - len(f))
        )
        return v[::-1]

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
        return (cls, list(map(lambda c: True if c == '1' else False, v)))

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


class Qfixed1_3(QfixedImp):
    BIT_SIZE = 4
    BIT_SIZE_INTEGER = 1
    BIT_SIZE_FACTORIAL = 3


class QfixedMeta(type):
    def __getitem__(cls, params):
        if isinstance(params, tuple) and len(params) == 2:
            i, f = params
            if isinstance(i, int) and isinstance(f, int) and i >= 0 and f >= 0:
                return f"Qfixed{i}_{f}"  # TODO: transform to type


class Qfixed(metaclass=QfixedMeta):
    pass
