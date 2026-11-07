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

from typing import Callable, Dict, List, Union

from sympy import Symbol, cse
from sympy.logic.boolalg import And, Boolean, Not, Or, Xor, simplify_logic

from ..ast2logic import BoolExpList
from . import SympyTransformer
from .exp_transformers import (
    remove_Implies,
    remove_ITE,
    remove_obvious_expr,
    transform_or2and,
    transform_or2xor,
)


def custom_simplify_logic(expr: Boolean) -> Boolean:
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
    res: BoolExpList = repl + list(zip(lsts[0], red))
    return res


def print_step(name: str):
    def _print_step(exps: BoolExpList) -> BoolExpList:
        print(name)
        for s, e in exps:
            print("\t", s, e)
        return exps

    return _print_step


class BoolOptimizerProfile:
    steps: List[Union[Callable[[BoolExpList], BoolExpList], SympyTransformer]]

    def __init__(self, steps: List):
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
        remove_obvious_expr(),
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
        remove_obvious_expr(),
        print_step("after"),
    ]
)


fastOptimizer = BoolOptimizerProfile(
    [
        remove_ITE(),
        remove_Implies(),
        transform_or2xor(),
        transform_or2and(),
        remove_obvious_expr(),
    ]
)
