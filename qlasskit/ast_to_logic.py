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
from typing import Dict, List, Tuple

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or, false, simplify_logic, true

from . import exceptions, utils
from .typing import Args, BoolExp, BoolExpList

Env = Dict[str, str]
LogicFun = Tuple[str, Args, str, BoolExpList]


def translate_arguments(args) -> Args:
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
    if isinstance(expr, ast.Name):
        if expr.id not in env:
            raise exceptions.UnboundException(expr.id)
        return Symbol(expr.id)

    elif isinstance(expr, ast.Subscript):
        if not isinstance(expr.value, ast.Name):
            raise exceptions.ExpressionNotHandledException(expr)
        elif not isinstance(expr.slice, ast.Constant):
            raise exceptions.ExpressionNotHandledException(expr)

        sn = f"{expr.value.id}.{expr.slice.value}"
        if sn not in env:
            raise exceptions.UnboundException(sn)
        return Symbol(sn)

    elif isinstance(expr, ast.BoolOp):

        def unfold(v_exps, op):
            return (
                op(v_exps[0], unfold(v_exps[1::], op)) if len(v_exps) > 1 else v_exps[0]
            )

        v_exps = [translate_expression(e_in, env) for e_in in expr.values]

        return unfold(v_exps, And if isinstance(expr.op, ast.And) else Or)

    elif isinstance(expr, ast.UnaryOp):
        if isinstance(expr.op, ast.Not):
            return Not(translate_expression(expr.operand, env))
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    elif isinstance(expr, ast.IfExp):
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

    elif isinstance(expr, ast.Constant):
        if expr.value is True:
            return true
        elif expr.value is False:
            return false
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    elif isinstance(expr, ast.Tuple):
        raise exceptions.ExpressionNotHandledException(expr)

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


def translate_statement(stmt, env: Env) -> Tuple[List[Tuple[str, BoolExp]], Env]:
    """Parse a statement"""
    # match stmt:
    if isinstance(stmt, ast.If):
        raise exceptions.StatementNotHandledException(stmt)

    elif isinstance(stmt, ast.Assign):
        raise exceptions.StatementNotHandledException(stmt)

    elif isinstance(stmt, ast.Return):
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


def translate_ast(fun) -> LogicFun:
    fun_name: str = fun.name

    # env contains names visible from the current scope
    env = {}

    args = translate_arguments(fun.args.args)
    # TODO: types are string; maybe a translate_type?
    for a_name, a_type in args:
        env[a_name] = a_type

    if not fun.returns:
        raise exceptions.NoReturnTypeException()
    fun_ret: str = fun.returns.id
    # TODO: handle complex-type returns

    exps = []
    for stmt in fun.body:
        s_exps, env = translate_statement(stmt, env)
        exps.append(s_exps)

    exps_flat = utils.flatten(exps)
    exps_simpl = list(map(lambda e: simplify_logic(e, form="cnf"), exps_flat))

    for n, e in exps_simpl:
        if e == true or e == false:
            raise exceptions.ConstantReturnException(n, e)

    return fun_name, args, fun_ret, exps_simpl
