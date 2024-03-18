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

import sys
from typing import Dict, List, Tuple

from sympy import Symbol
from sympy.logic.boolalg import Boolean

if sys.version_info < (3, 11):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

from ..types import BUILTIN_TYPES, Qint, Qtype  # noqa: F401, E402
from . import exceptions
from .typing import Arg, LogicFun

Binding: TypeAlias = Arg
TypeBinding = Tuple[str, Qtype]


class Env:
    def __init__(self) -> None:
        self.bindings: List[Binding] = []
        self.types: List[TypeBinding] = []
        self.defs: List[LogicFun] = []

        for t in BUILTIN_TYPES:
            self.bind_type((t.__name__, t))  # type: ignore

    def __repr__(self):
        return str((self.bindings, self.types, self.defs))

    def bind_type(self, bb: TypeBinding):
        if self.know_type(bb[0]):
            return
        self.types.append(bb)

    def know_type(self, type_name: str) -> bool:
        return len(list(filter(lambda x: x[0] == type_name, self.types))) == 1

    def gettype(self, type_name: str) -> Qtype:
        try:
            return list(filter(lambda x: x[0] == type_name, self.types))[0][1]
        except:
            raise exceptions.UnboundException(type_name, self)

    def know_function(self, fun_name: str) -> bool:
        return len(list(filter(lambda x: x[0] == fun_name, self.defs))) == 1

    def bind_function(self, deff: LogicFun):
        if self.know_type(deff[0]):
            return

        # Replace all the symbols in expr with def_name+symbol
        def arg_rename(a):
            a.name = f"{deff[0]}_{a.name}"
            a.bitvec = list(map(lambda b: f"{deff[0]}_{b}", a.bitvec))
            return a

        def exp_rename(se):
            s, e = se
            for x in e.free_symbols:
                e = e.subs(x, Symbol(f"{deff[0]}_{x.name}"))
            return (Symbol(f"{deff[0]}_{s.name}"), e)

        deff = (
            deff[0],  # name
            list(map(arg_rename, deff[1])),  # args
            deff[2],  # returns
            list(map(exp_rename, deff[3])),  # exprs
        )

        # Compress expr so it contains only len(returns) expressions
        d_exp: Dict[Symbol, Boolean] = {}
        n_exps = []
        for s, e in deff[3]:
            new_e = e.subs(d_exp)
            d_exp[s] = new_e
            n_exps.append((s, new_e))

        deff = (deff[0], deff[1], deff[2], n_exps[-len(deff[2]) :])

        self.defs.append(deff)

    def getdef(self, fun_name: str) -> LogicFun:
        try:
            return list(filter(lambda x: x[0] == fun_name, self.defs))[0]
        except:
            raise exceptions.UnboundException(fun_name, self)

    def bind(self, bb: Binding, rebind=False):
        if not rebind and bb.name in self:
            raise Exception("duplicate bind")

        if rebind:
            self.bindings.remove(self[bb.name])

        self.bindings.append(bb)

    def __contains__(self, key):
        return len(list(filter(lambda x: x.name == key, self.bindings))) == 1

    def __getitem__(self, key):
        try:
            return list(filter(lambda x: x.name == key, self.bindings))[0]
        except:
            raise exceptions.UnboundException(key, self)
