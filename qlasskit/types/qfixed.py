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

from typing import Any, Tuple, TypeVar, Generic

from .qint import Qint
from .qtype import Qtype, TExp

TI = TypeVar("TI")  # integer part
TF = TypeVar("TF")  # fractional part



class Qfixed(float, Qtype, Generic[TI, TF]):
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    @classmethod
    def const(cls, value: Any) -> TExp:
        val_s = str(value).split(".")
        if len(val_s) == 1:
            val_s.append("0")

        a = Qint._const(int(val_s[0]))
        b = Qint._const(int(val_s[1]))
        return Qfixed[a[0], b[0]], [a[1], b[1]]


    # Operations

    @classmethod
    def add(cls, tleft: TExp, tright: TExp) -> TExp:
        """Add two Qfixed"""
        pass