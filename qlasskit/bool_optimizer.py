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

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from .ast2logic import Arg, BoolExpList


def remove_const_exps(exps: BoolExpList, fun_ret: Arg) -> BoolExpList:
    """Remove const exps (replace a = True, b = ~a or c with b = c)"""
    const: Dict[Symbol, Boolean] = {}
    n_exps: BoolExpList = []
    for i in range(len(exps)):
        (s, e) = exps[i]
        e = e.subs(const)
        if (e == False or e == True) and i < (len(exps) - len(fun_ret)):  # noqa: E712
            const[s] = e
        else:
            if s in const:
                del const[s]
            n_exps.append((s, e))

    return n_exps


# def subsitute_exps(exps: BoolExpList, fun_ret: Arg) -> BoolExpList:
#     """Subsitute exps (replace a = ~a, a = ~a, a = ~a => a = ~a)"""
#     const: Dict[Symbol, Boolean] = {}
#     n_exps: BoolExpList = []
#     print(exps)

#     for i in range(len(exps)):
#         (s, e) = exps[i]
#         e = e.subs(const)
#         const[s] = e

#         for x in e.free_symbols:
#             if x in const:
#                 n_exps.append((x, const[x]))
#                 del const[x]

#     for (s,e) in const.items():
#         if s == e:
#             continue

#         n_exps.append((s,e))

#     print(n_exps)
#     print()
#     print()
#     return n_exps


def remove_unnecessary_assigns(exps: BoolExpList) -> BoolExpList:
    """Remove exp like: __a.0 = a.0, ..., a.0 = __a.0"""
    n_exps: BoolExpList = []

    def should_add(s, e, n_exps2):
        ename = f"__{s.name}"
        if e.name == ename:
            for s1, e1 in n_exps2[::-1]:
                if s1.name == ename:
                    if isinstance(e1, Symbol) and e1.name == s.name:
                        n_exps2.remove((s1, e1))
                        return False
                    else:
                        return True
        return True

    for s, e in exps:
        if not isinstance(e, Symbol) or should_add(s, e, n_exps):
            n_exps.append((s, e))

    return n_exps


def merge_unnecessary_assigns(exps: BoolExpList) -> BoolExpList:
    """Translate exp like: __a.0 = !a, a = __a.0 ===> a = !a"""
    n_exps: BoolExpList = []

    for s, e in exps:
        if len(n_exps) >= 1 and n_exps[-1][0] == e:
            old = n_exps.pop()
            n_exps.append((s, old[1]))
        else:
            n_exps.append((s, e))

    return n_exps


# [(h, a_list.0.0 & a_list.0.1), (h, a_list.1.0 & a_list.1.1 & h), (h, a_list.2.0 & a_list.2.1 & h), (_ret, a_list.3.0 & a_list.3.1 & h)]
# TO
#(_ret, a_list_3_0 & a_list_3_1 & a_list_2_0 & a_list_2_1 & a_list_1_0 & a_list_1_1 & a_list_0_0 & a_list_0_1)
