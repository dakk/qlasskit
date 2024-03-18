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

from typing import Dict

from sympy import Symbol, cse
from sympy.logic.boolalg import And, Boolean, Not, Or, Xor, simplify_logic

from ..ast2logic import BoolExpList
from . import SympyTransformer
from .exp_transformers import (
    remove_Implies,
    remove_ITE,
    transform_or2and,
    transform_or2xor,
)


def custom_simplify_logic(expr):
    if isinstance(expr, Xor):
        return expr
    elif isinstance(expr, (And, Or, Not)):
        args = [custom_simplify_logic(arg) for arg in expr.args]
        return type(expr)(*args)
    else:
        return simplify_logic(expr)


def merge_expressions(exps: BoolExpList) -> BoolExpList:
    n_exps = []
    emap: Dict[Symbol, Boolean] = {}

    for s, e in exps:
        e = e.xreplace(emap)
        e = custom_simplify_logic(e)

        if s.name[0:4] != "_ret":
            emap[s] = e
        else:
            n_exps.append((s, e))

    return n_exps


def apply_cse(exps: BoolExpList) -> BoolExpList:
    lsts = list(zip(*exps))
    repl, red = cse(list(lsts[1]))
    res = repl + list(zip(lsts[0], red))
    return res


def print_step(name: str):
    def _print_step(exps: BoolExpList) -> BoolExpList:
        print(name)
        for s, e in exps:
            print("\t", s, e)
        return exps

    return _print_step


class BoolOptimizerProfile:
    def __init__(self, steps):
        self.steps = steps

    def apply(self, exps):
        for opt in self.steps:
            if isinstance(opt, SympyTransformer):
                exps = list(map(lambda e: (e[0], opt.visit(e[1])), exps))
            else:
                exps = opt(exps)
        return exps


defaultOptimizer = BoolOptimizerProfile(
    [
        merge_expressions,
        apply_cse,
        remove_ITE(),
        remove_Implies(),
        transform_or2xor(),
        transform_or2and(),
    ]
)


defaultOptimizerDebug = BoolOptimizerProfile(
    [
        print_step("before"),
        merge_expressions,
        apply_cse,
        remove_ITE(),
        remove_Implies(),
        transform_or2xor(),
        transform_or2and(),
        print_step("after"),
    ]
)


fastOptimizer = BoolOptimizerProfile(
    [
        remove_ITE(),
        remove_Implies(),
        transform_or2xor(),
        transform_or2and(),
    ]
)
