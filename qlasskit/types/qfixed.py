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

from typing import Any, Tuple, TypeVar

from .qint import Qint
from .qtype import TExp

TI = TypeVar("TI")  # integer part
TF = TypeVar("TF")  # fractional part


class QfixedMeta(type):
    def __getitem__(cls, params):
        if isinstance(params, tuple) and len(params) == 2:
            TI, TF = params

            if isinstance(TI, int):
                bs = TI
                TI = Qint
                TI.BIT_SIZE = bs

            if isinstance(TF, int):
                bs = TF
                TF = Qint
                TF.BIT_SIZE = bs

            assert issubclass(TI, Qint)
            assert issubclass(TF, Qint)

            return (
                TI,
                TF,
            )


class Qfixed(metaclass=QfixedMeta):
    @classmethod
    def const(cls, value: Any) -> TExp:
        val_s = str(value).split(".")
        if len(val_s) == 1:
            val_s.append("0")

        a = Qint._const(int(val_s[0]))
        b = Qint._const(int(val_s[1]))
        return Tuple[a[0], b[0]], a[1] + b[1]
