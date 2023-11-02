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

from typing import Any, get_args

from sympy.logic import Not, Xor, And, Or


def _neq(a, b):
    return Xor(a, b)


def _eq(a, b):
    return Not(_neq(a, b))


def _half_adder(a, b):  # Carry x Sum
    return And(a, b), Xor(a, b)


def _full_adder(c, a, b):  # Carry x Sum
    return Or(And(a, b), And(b, c), And(a, c)), Xor(a, b, c)


from .qtype import Qtype, TExp, TType  # noqa: F401, E402
from .qbool import Qbool  # noqa: F401, E402
from .qlist import Qlist  # noqa: F401, E402
from .qint import Qint, Qint2, Qint4, Qint8, Qint12, Qint16  # noqa: F401, E402

BUILTIN_TYPES = [Qint2, Qint4, Qint8, Qint12, Qint16, Qlist]


def const_to_qtype(value: Any):
    if isinstance(value, int):
        for det_type in [Qint2, Qint4, Qint8, Qint12, Qint16]:
            if value < 2**det_type.BIT_SIZE:
                return det_type.const(value)

        raise Exception(f"Constant value is too big: {value}")

    return None


def type_repr(typ) -> str:
    if hasattr(typ, "__name__"):
        return typ.__name__
    elif len(get_args(typ)) > 0:
        args = [type_repr(a) for a in get_args(typ)]
        if all([args[0] == a for a in args[1:]]):
            return f"Qlist[{args[0]}, {len(args)}]"
        else:
            return f"Tuple[{','.join(args)}]"
    else:
        raise Exception(f"Unable to represent type: {typ}")
