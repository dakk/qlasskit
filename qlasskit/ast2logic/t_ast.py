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
    [env.bind_type((t.__name__, t)) for t in types]

    args: Args = translate_arguments(fun.args.args, env)

    [env.bind(arg) for arg in args]
    [env.bind_function(f) for f in defs]

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
