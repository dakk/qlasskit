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
# isort:skip_file

from typing import Any

from sympy.logic import Not, Xor


def _neq(a, b):
    return Xor(a, b)


def _eq(a, b):
    return Not(_neq(a, b))


from .qtype import Qtype, TExp, TType  # noqa: F401, E402
from .qbool import Qbool  # noqa: F401, E402
from .qint import Qint, Qint2, Qint4, Qint8, Qint12, Qint16  # noqa: F401, E402

BUILTIN_TYPES = [Qint2, Qint4, Qint8, Qint12, Qint16]


def const_to_qtype(value: Any):
    if isinstance(value, int):
        for det_type in [Qint2, Qint4, Qint8, Qint12, Qint16]:
            if value < 2**det_type.BIT_SIZE:
                return det_type.const(value)

        raise Exception(f"Constant value is too big: {value}")

    return None
