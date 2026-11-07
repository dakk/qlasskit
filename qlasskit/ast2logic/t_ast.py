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

from typing import List

from sympy.logic import simplify_logic

from . import (
    Env,
    exceptions,
    flatten,
    translate_argument,
    translate_arguments,
    translate_statement,
)
from .typing import Args, LogicFun


def translate_ast(fun, types: List = [], defs: List[LogicFun] = []) -> LogicFun:
    fun_name: str = fun.name

    # env contains names visible from the current scope
    env = Env()
    for t in types:
        env.bind_type((t.__name__, t))

    args: Args = translate_arguments(fun.args.args, env)

    for arg in args:
        env.bind(arg)

    for f in defs:
        env.bind_function(f)

    if not fun.returns:
        raise exceptions.NoReturnTypeException()

    ret_ = translate_argument(fun.returns, env, base="_ret")

    exps = []
    for stmt in fun.body:
        s_exps, env = translate_statement(stmt, env, ret_.ttype)
        exps.append(s_exps)

    exps_flat = flatten(exps)
    exps_simpl = list(map(lambda e: simplify_logic(e, form="cnf"), exps_flat))

    # for n, e in exps_simpl:
    #     if e == true or e == false:
    #         print(f"Warning: expression {n} is returning a costant: {e}")

    return fun_name, args, ret_, exps_simpl
