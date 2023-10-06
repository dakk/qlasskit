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
import ast
from typing import Any, List, Tuple

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or, false, true
from sympy.logic.boolalg import Boolean
from typing_extensions import TypeAlias

from . import Env, exceptions

TType: TypeAlias = object


def type_of_exp(vlist, base, env, res=[]) -> Tuple[List[Symbol], Env]:
    """Type inference for expressions: iterate over val, and decompose to bool"""
    if isinstance(vlist, list):
        i = 0
        res = []
        for in_val in vlist:
            r_new, env = type_of_exp(in_val, f"{base}.{i}", env, res)
            if isinstance(r_new, list):
                res.extend(r_new)
            else:
                res.append(r_new)
            i += 1
        return res, env
    else:
        new_symb = (f"{base}", vlist)
        env.append(new_symb[0])
        return [new_symb], env


def translate_expression(expr, env: Env) -> Tuple[TType, Boolean]:  # noqa: C901
    """Translate an expression"""

    # Name reference
    if isinstance(expr, ast.Name):
        if expr.id not in env:
            # Handle complex types
            rl = []
            for sym in env:
                if sym[0 : (len(expr.id) + 1)] == f"{expr.id}.":
                    rl.append(Symbol(sym))

            if len(rl) == 0:
                raise exceptions.UnboundException(expr.id, env)

            return (Any, rl)  # TODO: typecheck
        return (Any, Symbol(expr.id))  # TODO: typecheck

    # Subscript: a[0][1]
    elif isinstance(expr, ast.Subscript):

        def unroll_subscripts(sub, st):
            if isinstance(sub.value, ast.Subscript):
                st = f"{sub.slice.value.value}{'.' if st else ''}{st}"
                return unroll_subscripts(sub.value, st)
            elif isinstance(sub.value, ast.Name):
                return f"{sub.value.id}.{sub.slice.value.value}.{st}"

        if not isinstance(expr.slice, ast.Index):
            raise exceptions.ExpressionNotHandledException(expr)
        elif not isinstance(expr.slice.value, ast.Constant):
            raise exceptions.ExpressionNotHandledException(expr)

        if isinstance(expr.value, ast.Name):
            sn = f"{expr.value.id}.{expr.slice.value.value}"
        else:
            sn = unroll_subscripts(expr, "")

        if sn not in env:
            raise exceptions.UnboundException(sn, env)

        return (Any, Symbol(sn))

    # Boolop: and, or
    elif isinstance(expr, ast.BoolOp):

        def unfold(v_exps, op):
            return (
                op(v_exps[0], unfold(v_exps[1::], op)) if len(v_exps) > 1 else v_exps[0]
            )

        v_exps = [
            translate_expression(e_in, env)[1] for e_in in expr.values
        ]  # TODO: typecheck

        return (bool, unfold(v_exps, And if isinstance(expr.op, ast.And) else Or))

    # Unary: not
    elif isinstance(expr, ast.UnaryOp):
        if isinstance(expr.op, ast.Not):
            return (
                bool,
                Not(translate_expression(expr.operand, env)[1]),
            )  # TODO: typecheck
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # If expression
    elif isinstance(expr, ast.IfExp):
        return (
            bool,
            ITE(
                translate_expression(expr.test, env)[1],  # TODO: typecheck
                translate_expression(expr.body, env)[1],  # TODO: typecheck
                translate_expression(expr.orelse, env)[1],  # TODO: typecheck
            ),
        )

    # Constant
    elif isinstance(expr, ast.Constant):
        if expr.value is True:
            return (bool, true)
        elif expr.value is False:
            return (bool, false)
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # Tuple
    elif isinstance(expr, ast.Tuple):
        elts = [
            translate_expression(elt, env)[1] for elt in expr.elts
        ]  # TODO: typecheck
        return (Any, elts)  # TODO: typecheck

    # Compare operator
    elif isinstance(expr, ast.Compare):
        # Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        raise exceptions.ExpressionNotHandledException(expr)

    # Lambda
    # Dict
    # Set
    # Call
    # List
    # op Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift | RShift
    # | BitOr | BitXor | BitAnd | FloorDiv

    else:
        raise exceptions.ExpressionNotHandledException(expr)
