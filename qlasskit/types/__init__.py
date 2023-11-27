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

from typing import Any, List, Union, Optional, get_args

from sympy.logic import Not, Xor, And


def _neq(a, b):
    return Xor(a, b)


def _eq(a, b):
    return Not(_neq(a, b))


def _half_adder(a, b):  # Carry x Sum
    return And(a, b), Xor(a, b)


def _full_adder(c, a, b):  # Carry x Sum
    return (a & b) ^ (a ^ b) & c, Xor(Xor(a, b), c)

    # from ..boolquant import H, CX, MCX
    # from sympy import Symbol
    # o = Symbol('new_qubit')
    # o = MCX(a, b, o)
    # b = CX(a, b)
    # o = MCX(b, c, o)
    # c = CX(b,c)
    # return c, o


from .qtype import Qtype, TExp, TType  # noqa: F401, E402
from .qbool import Qbool  # noqa: F401, E402
from .qlist import Qlist  # noqa: F401, E402
from .qmatrix import Qmatrix  # noqa: F401, E402
from .qint import Qint, Qint2, Qint3, Qint4, Qint8, Qint12, Qint16  # noqa: F401, E402

BUILTIN_TYPES = [Qint2, Qint3, Qint4, Qint8, Qint12, Qint16, Qlist, Qmatrix]


def const_to_qtype(value: Any) -> TExp:
    if isinstance(value, int):
        for det_type in [Qint2, Qint4, Qint8, Qint12, Qint16]:  # Qint3
            if value < 2**det_type.BIT_SIZE:
                return det_type.const(value)

        raise Exception(f"Constant value is too big: {value}")

    raise Exception(f"Unable to infer type of constant: {value}")


def type_repr(typ) -> str:
    if hasattr(typ, "__name__"):
        if len(get_args(typ)) == 0:
            return typ.__name__

        args = [type_repr(a) for a in get_args(typ)]
        return f"{typ.__name__}[{','.join(args)}]"

    elif len(get_args(typ)) > 0:  # This is for python = 3.8
        args = [type_repr(a) for a in get_args(typ)]
        if all([args[0] == a for a in args[1:]]):
            return f"Qlist[{args[0]}, {len(args)}]"
        else:
            return f"Tuple[{','.join(args)}]"
    else:
        raise Exception(f"Unable to represent type: {typ}")


def format_outcome(
    out: Union[str, int, List[bool]], out_len: Optional[int] = None
) -> List[bool]:
    if isinstance(out, str):
        return format_outcome([True if c == "1" else False for c in out], out_len)
    elif isinstance(out, int):
        return format_outcome(str(bin(out))[2:], out_len)
    elif isinstance(out, List):
        if out_len is None:
            out_len = len(out)

        if len(out) < out_len:
            out += [False] * (out_len - len(out))

        return out
    raise Exception(f"Invalid format: {out}")


def interpret_as_qtype(
    out: Union[str, int, List[bool]], qtype, out_len: Optional[int] = None
) -> Any:
    out = list(reversed(format_outcome(out, out_len)))

    def _getsize(x):
        if hasattr(x, "BIT_SIZE"):
            return x.BIT_SIZE
        elif len(get_args(x)) > 0:
            size = 0
            for x in get_args(x):
                size += _getsize(x)
            return size
        else:
            return 1

    def _interpret(out, qtype, out_len):
        if hasattr(qtype, "from_bool"):
            return qtype.from_bool(out[0:out_len])  # type: ignore
        elif qtype == bool:
            return out[0]
        else:  # Tuple
            idx_s = 0
            values = []
            for x in get_args(qtype):
                len_a = _getsize(x)
                values.append(_interpret(out[idx_s : idx_s + len_a], x, len_a))
                idx_s += len_a

            return tuple(values)

    return _interpret(out, qtype, out_len)
