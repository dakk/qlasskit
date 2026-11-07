# Copyright (C) 2023-2026 Davide Gessa
# This file is part of Qlasskit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
from typing import Any, Dict, List, Tuple

from sympy import Symbol
from sympy.logic.boolalg import Boolean

if sys.version_info < (3, 11):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias  # novermin

from ..types import BUILTIN_TYPES, Qint, Qtype  # noqa: F401, E402
from . import exceptions
from .typing import Arg, LogicFun

Binding: TypeAlias = Arg
TypeBinding = Tuple[str, Qtype]


class Env:
    bindings: List[Binding]
    types: List[TypeBinding]
    defs: List[LogicFun]
    consts: Dict[str, Any]

    def __init__(self) -> None:
        self.bindings = []
        self.types = []
        self.defs = []
        self.consts = {}

        for t in BUILTIN_TYPES:
            self.bind_type((t.__name__, t))  # type: ignore

    def __repr__(self) -> str:
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

    def bind_function(self, deff: LogicFun) -> None:
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

    def set_constant(self, name: str, value: Any) -> None:
        self.consts[name] = value

    def get_constant(self, name: str) -> Any:
        return self.consts[name]

    def has_constant(self, name: str) -> bool:
        return name in self.consts

    def remove_constant(self, name: str) -> None:
        self.consts.pop(name, None)

    def bind(self, bb: Binding, rebind=False) -> None:
        if not rebind and bb.name in self:
            raise Exception("duplicate bind")

        if rebind:
            self.bindings.remove(self[bb.name])

        self.bindings.append(bb)

    def __contains__(self, key: str) -> bool:
        return len(list(filter(lambda x: x.name == key, self.bindings))) == 1

    def __getitem__(self, key: str) -> Binding:
        try:
            return list(filter(lambda x: x.name == key, self.bindings))[0]
        except:
            raise exceptions.UnboundException(key, self)
