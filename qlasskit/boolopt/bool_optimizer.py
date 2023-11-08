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

from typing import Dict

from sympy import Symbol, cse
from sympy.logic.boolalg import Boolean, simplify_logic

from ..ast2logic import BoolExpList
from . import SympyTransformer, deprecated
from .exp_transformers import (
    remove_Implies,
    remove_ITE,
    transform_or2and,
    transform_or2xor,
)


def merge_expressions(exps: BoolExpList) -> BoolExpList:
    n_exps = []
    emap: Dict[Symbol, Boolean] = {}

    for s, e in exps:
        e = e.xreplace(emap)

        if s.name[0:4] != "_ret":
            emap[s] = simplify_logic(e)
        else:
            n_exps.append((s, simplify_logic(e)))

    return n_exps


def apply_cse(exps: BoolExpList) -> BoolExpList:
    lsts = list(zip(*exps))
    repl, red = cse(list(lsts[1]))
    res = repl + list(zip(lsts[0], red))
    return res


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


bestWorkingOptimizer = BoolOptimizerProfile(
    [
        merge_expressions,
        apply_cse,
        remove_ITE(),
        remove_Implies(),
        transform_or2xor(),
        transform_or2and(),
    ]
)


deprecatedWorkingOptimizer = BoolOptimizerProfile(
    [
        deprecated.remove_const_exps,
        deprecated.remove_unnecessary_assigns,
        deprecated.merge_unnecessary_assigns,
        merge_expressions,
        apply_cse,
        remove_ITE(),
        remove_Implies(),
        transform_or2xor(),
        transform_or2and(),
    ]
)
