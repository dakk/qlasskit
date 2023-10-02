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
import ast
from typing import List

from .. import exceptions, utils
from ..typing import Args


def translate_argument(ann, base="") -> List[str]:
    def to_name(a):
        return a.attr if isinstance(a, ast.Attribute) else a.id

    # Tuple
    if isinstance(ann, ast.Subscript) and ann.value.id == "Tuple":  # type: ignore
        al = []
        ind = 0
        for i in ann.slice.value.elts:  # type: ignore
            if isinstance(i, ast.Name) and to_name(i) == "bool":
                al.append(f"{base}.{ind}")
            else:
                inner_list = translate_argument(i, base=f"{base}.{ind}")
                al.extend(inner_list)
            ind += 1
        return al

    # QintX
    elif to_name(ann)[0:4] == "Qint":
        n = int(to_name(ann)[4::])
        arg_list = [f"{base}.{i}" for i in range(n)]
        # arg_list.append((f"{base}{arg.arg}", n))
        return arg_list

    # Bool
    elif to_name(ann) == "bool":
        return [f"{base}"]

    else:
        raise exceptions.UnknownTypeException(ann)


def translate_arguments(args) -> Args:
    """Parse an argument list"""
    args_unrolled = map(
        lambda arg: translate_argument(arg.annotation, base=arg.arg), args
    )
    return utils.flatten(list(args_unrolled))
