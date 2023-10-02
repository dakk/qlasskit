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

from typing import Dict, List, Tuple, Union

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or

BoolExp = Union[Symbol, And, Or, Not, ITE, bool]
Args = List[Tuple[str, str]]
BoolExpList = List[Tuple[Symbol, BoolExp]]
Env = Dict[Symbol, str]
LogicFun = Tuple[str, Args, Symbol, BoolExpList]


class Qtype:
    def __init__(self):
        self.bit_size

    def to_bool(self):
        raise Exception("abstract")


# class Qbool(bool, Qtype):
#     def __init__(self, value):
#         super().__init__()
#         self.value = value
#         self.bit_size = 1

#     def to_bool(self):
#         return self.value


class Qint(int, Qtype):
    def __init__(self, value, bit_size=8):
        super().__init__()
        self.value = value
        self.bit_size = bit_size


class Qint2(Qint):
    def __init__(self, value):
        super().__init__(value, bit_size=2)


class Qint4(Qint):
    def __init__(self, value):
        super().__init__(value, bit_size=4)


class Qint8(Qint):
    def __init__(self, value):
        super().__init__(value, bit_size=8)


class Qint12(Qint):
    def __init__(self, value):
        super().__init__(value, bit_size=12)


class Qint16(Qint):
    def __init__(self, value):
        super().__init__(value, bit_size=16)


# class Qpair
# class Qlist
# class Qfixed
