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
from sympy.logic import false, simplify_logic, true

from ..typing import Args, LogicFun
from . import (
    Env,
    exceptions,
    flatten,
    translate_argument,
    translate_arguments,
    translate_statement,
)


def translate_ast(fun) -> LogicFun:
    fun_name: str = fun.name

    # env contains names visible from the current scope
    env = Env()

    args: Args = translate_arguments(fun.args.args)

    [env.bind(arg) for arg in args]

    if not fun.returns:
        raise exceptions.NoReturnTypeException()

    ret_ = translate_argument(fun.returns)  # TODO: we need to preserve this
    ret_size = len(ret_)

    exps = []
    for stmt in fun.body:
        s_exps, env = translate_statement(stmt, env)
        exps.append(s_exps)

    exps_flat = flatten(exps)
    exps_simpl = list(map(lambda e: simplify_logic(e, form="cnf"), exps_flat))

    for n, e in exps_simpl:
        if e == true or e == false:
            raise exceptions.ConstantReturnException(n, e)

    return fun_name, args, ret_size, exps_simpl
