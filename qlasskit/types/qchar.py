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

from typing import Any, List

from sympy.logic import And, Or, false, true

from . import _eq, _neq
from .qint import Qint
from .qtype import Qtype, TExp


class Qchar(str, Qtype):
    BIT_SIZE = 8

    def __init__(self, value: str):
        super().__init__()
        assert len(value) == 1
        self.value = value[0]

    def to_bin(self) -> str:
        s = bin(ord(self.value))[2:][0 : self.BIT_SIZE]
        return ("0" * (self.BIT_SIZE - len(s)) + s)[::-1]

    def to_amplitudes(self) -> List[float]:
        ampl = [0.0] * 2**self.BIT_SIZE
        ampl[ord(self.value)] = 1
        return ampl

    @classmethod
    def from_bool(cls, v: List[bool]):
        bin_str = "".join(map(lambda x: "1" if x else "0", v))
        return cls(chr(int(bin_str[::-1], 2)))

    @classmethod
    def comparable(cls, other_type=None) -> bool:
        return other_type == cls or issubclass(other_type, Qint)

    @classmethod
    def fill(cls, v: TExp) -> TExp:
        if len(v[1]) < cls.BIT_SIZE:  # type: ignore
            v = (
                cls,
                v[1] + (cls.BIT_SIZE - len(v[1])) * [False],  # type: ignore
            )
        return v

    @classmethod
    def const(cls, value: Any) -> TExp:
        assert len(value) == 1
        cval = list(
            map(lambda c: True if c == "1" else False, bin(ord(value))[2:][::-1])
        )  # [::-1]
        return cls.fill((cls, cval))

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
