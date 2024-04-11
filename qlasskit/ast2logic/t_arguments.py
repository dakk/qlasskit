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
import ast
from typing import List, Tuple

from ..types import *  # noqa: F401, F403
from ..types import TType
from . import Env, exceptions
from .typing import Arg, Args


def translate_argument(ann, env, base="") -> Arg:  # noqa: C901
    def to_name(a):
        if isinstance(a, ast.Attribute):
            return a.attr
        elif isinstance(a, ast.Subscript):  # for Qfixed and similar
            if isinstance(a.slice, ast.Constant):
                t = f"{a.slice.value}"
            else:
                t = "_".join(f"{e.value}" for e in a.slice.elts)  # type: ignore
            return f"{a.value.id}{t}"  # type: ignore
        else:
            return a.id

    ttypes: List[TType] = []

    # Tuple
    if isinstance(ann, ast.Subscript) and ann.value.id == "Tuple":  # type: ignore
        al = []
        ind = 0

        if hasattr(ann.slice, "elts"):
            _elts = ann.slice.elts  # type: ignore
        else:
            _elts = [ann.slice]

        for i in _elts:  # type: ignore
            if isinstance(i, ast.Name) and to_name(i) == "bool":
                al.append(f"{base}.{ind}")
                ttypes.append(bool)
            else:
                inner_arg = translate_argument(i, env, base=f"{base}.{ind}")
                ttypes.append(inner_arg.ttype)
                al.extend(inner_arg.bitvec)
            ind += 1
        ttypes_t = tuple(ttypes)
        return Arg(base, Tuple[ttypes_t], al)  # type: ignore

    elif isinstance(ann, ast.Tuple):
        al = []
        ind = 0

        _elts = ann.elts  # type: ignore

        for i in _elts:  # type: ignore
            if isinstance(i, ast.Name) and to_name(i) == "bool":
                al.append(f"{base}.{ind}")
                ttypes.append(bool)
            else:
                inner_arg = translate_argument(i, env, base=f"{base}.{ind}")
                ttypes.append(inner_arg.ttype)
                al.extend(inner_arg.bitvec)
            ind += 1
        ttypes_t = tuple(ttypes)
        return Arg(base, Tuple[ttypes_t], al)  # type: ignore

    # Bool
    elif to_name(ann) == "bool":
        return Arg(base, bool, [f"{base}"])

    # Check if it is a know type in env
    elif env.know_type(to_name(ann)):
        t = env.gettype(to_name(ann))
        arg_list = [f"{base}.{i}" for i in range(t.BIT_SIZE)]
        return Arg(base, t, arg_list)

    else:
        raise exceptions.UnknownTypeException(ann)


def translate_arguments(args, env: Env) -> Args:
    """Parse an argument list"""
    args_unrolled = map(
        lambda arg: translate_argument(arg.annotation, env=env, base=arg.arg), args
    )
    return list(args_unrolled)
