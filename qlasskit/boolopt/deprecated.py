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
from sympy.logic.boolalg import Boolean, simplify_logic

from ..ast2logic import BoolExpList


def remove_const_exps(exps: BoolExpList) -> BoolExpList:
    """Remove const exps (replace a = True, b = ~a or c with b = c)"""
    const: Dict[Symbol, Boolean] = {}
    n_exps: BoolExpList = []
    for i in range(len(exps)):
        (s, e) = exps[i]
        e = e.subs(const)
        if (e == False or e == True) and s.name[0:4] != "_ret":  # noqa: E712
            const[s] = e
        else:
            if s in const:
                del const[s]
            n_exps.append((s, e))

    return n_exps


# def subsitute_exps(exps: BoolExpList) -> BoolExpList:
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
            for s1, e1 in reversed(n_exps2):
                if s1.name == ename:
                    if isinstance(e1, Symbol) and e1.name == s.name:
                        if all([s1 not in xe.free_symbols for (xs, xe) in n_exps]):
                            n_exps2.remove((s1, e1))
                            return False
                        return True
                    else:
                        return True
        return True

    for s, e in exps:
        if not isinstance(e, Symbol) or should_add(s, e, n_exps):
            n_exps.append((s, e))

    return n_exps

    # for s, e in exps:
    #     n_exps2 = []
    #     ename = f"__{s.name}"
    #     n_exps.append((s, e))

    #     for s_, e_ in reversed(n_exps):
    #         if s_.name == ename:
    #             continue
    #         else:
    #             _replaced = e_.subs(Symbol(ename), Symbol(s.name))
    #             if s_ != _replaced:
    #                 n_exps2.append((s_, _replaced))

    #     n_exps = n_exps2[::-1]

    # return n_exps


def merge_unnecessary_assigns(exps: BoolExpList) -> BoolExpList:
    """Translate exp like: __a.0 = !a, a = __a.0 ===> a = !a"""
    n_exps: BoolExpList = []
    rep_d = {}

    for s, e in exps:
        if len(n_exps) >= 1 and n_exps[-1][0] == e:  # and n_exps[-1][0].name[2:] == s:
            old = n_exps.pop()
            rep_d[old[0]] = old[1]
            n_exps.append((s, e.subs(rep_d)))
        else:
            n_exps.append((s, e.subs(rep_d)))

    return n_exps


def remove_unnecessary_aliases(exps: BoolExpList) -> BoolExpList:
    """Translate exps like: (__d.0, a), (d.0, __d.0 & a) to => (d.0, a & a)"""
    n_exps: BoolExpList = []
    rep_d = {}

    for s, e in exps:
        if len(n_exps) >= 1 and n_exps[-1][0] in e.free_symbols:
            old = n_exps.pop()
            rep_d[old[0]] = old[1]
            n_exps.append((s, e.subs(rep_d)))
        else:
            n_exps.append((s, e.subs(rep_d)))

    return n_exps


def remove_aliases(exps: BoolExpList) -> BoolExpList:
    aliases = {}
    n_exps = []
    for s, e in exps:
        if isinstance(e, Symbol):
            aliases[s] = e
        elif s in aliases:
            del aliases[s]
            n_exps.append((s, e.subs(aliases)))
        else:
            n_exps.append((s, e.subs(aliases)))

    return n_exps


def s2_mega(exps: BoolExpList) -> BoolExpList:
    n_exps: BoolExpList = []
    exp_d = {}

    for s, e in exps:
        exp_d[s] = e
        n_exps.append((s, e.subs(exp_d)))

    s_count = {}
    exps = n_exps

    for s, e in exps:
        if s.name not in s_count:
            s_count[s.name] = 0

        for x in e.free_symbols:
            if x.name in s_count:
                s_count[x.name] += 1

    n_exps = []
    for s, e in exps:
        if s_count[s.name] > 0 or s.name[0:4] == "_ret":
            n_exps.append((s, e))

    return n_exps


def exps_simplify(exps: BoolExpList) -> BoolExpList:
    return list(map(lambda e: (e[0], simplify_logic(e[1])), exps))


# [(h, a_list.0.0 & a_list.0.1), (h, a_list.1.0 & a_list.1.1 & h),
# (h, a_list.2.0 & a_list.2.1 & h), (_ret, a_list.3.0 & a_list.3.1 & h)]
# TO
# (_ret, a_list_3_0 & a_list_3_1 & a_list_2_0 & a_list_2_1 & a_list_1_0 & a_list_1_1 &
# a_list_0_0 & a_list_0_1)
