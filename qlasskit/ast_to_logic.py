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
from typing import Dict, List, Tuple, Union

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or, false, true

from . import exceptions, utils

BoolExp = Union[Symbol, And, Or, Not, ITE, bool]
Env = Dict[str, str]


def translate_arguments(args) -> List[Tuple[str, str]]:
    """Parse an argument list"""

    def map_arg(arg):
        def to_name(a):
            return a.attr if isinstance(a, ast.Attribute) else a.id

        if isinstance(arg.annotation, ast.Subscript):
            al = []
            for i in arg.annotation.slice.elts:
                al.append((f"{arg.arg}.{len(al)}", to_name(i)))
            return al
        elif to_name(arg.annotation)[0:3] == "Int":
            n = int(to_name(arg.annotation)[3::])
            arg_list = [(f"{arg.arg}.{i}", "bool") for i in range(n)]
            arg_list.append((f"{arg.arg}", n))
            return arg_list
        else:
            return [(arg.arg, to_name(arg.annotation))]

    return utils.flatten(list(map(map_arg, args)))


def translate_expression(expr, env: Env) -> BoolExp:  # noqa: C901
    """Translate an expression"""
    if expr == ast.Name():
        if expr.id not in env:
            raise exceptions.UnboundException(expr.id)
        return Symbol(expr.id)

    elif expr == ast.Subscript():
        sn = f"{expr.value.id}.{expr.slice.value}"
        if sn not in env:
            raise exceptions.UnboundException(sn)
        return Symbol(sn)

    elif expr == ast.BoolOp():

        def unfold(v_exps, op):
            return (
                op(v_exps[0], unfold(v_exps[1::], op)) if len(v_exps) > 1 else v_exps[0]
            )

        v_exps = [translate_expression(e_in, env) for e_in in expr.values]

        return unfold(v_exps, And if expr.op == ast.And() else Or)

    elif expr == ast.UnaryOp():
        if expr.op == Not():
            return Not(translate_expression(expr.operand, env))
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    elif expr == ast.IfExp():
        # (condition) and (true_value) or (not condition) and (false_value)
        # return Or(
        #     And(translate_expression(expr.test, env), translate_expression(expr.body, env)),
        #     And(Not(translate_expression(expr.test, env)), translate_expression(expr.orelse, env))
        # )
        return ITE(
            translate_expression(expr.test, env),
            translate_expression(expr.body, env),
            translate_expression(expr.orelse, env),
        )

    elif expr == ast.Constant():
        if expr.value is True:
            return true
        elif expr.value is False:
            return false
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    elif expr == ast.Tuple():
        raise exceptions.ExpressionNotHandledException(expr)

    elif expr == ast.Compare():
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


def translate_statement(stmt, env: Env) -> Tuple[List[Tuple[str, BoolExp]], Env]:
    """Parse a statement"""
    # match stmt:
    if stmt == ast.If():
        raise exceptions.StatementNotHandledException(stmt)

    elif stmt == ast.Assign():
        raise exceptions.StatementNotHandledException(stmt)

    elif stmt == ast.Return():
        vexp = translate_expression(stmt.value, env)
        return [("_ret", vexp)], env

        # FunctionDef
        # For
        # While
        # With
        # Expr
        # Pass
        # Break
        # Continue
        # Match

    else:
        raise exceptions.StatementNotHandledException(stmt)
