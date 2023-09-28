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

Env = Dict[Symbol, str]
LogicFun = Tuple[str, Args, Symbol, BoolExpList]


def translate_argument(ann, base="") -> List[Tuple[str, str]]:
    def to_name(a):
        return a.attr if isinstance(a, ast.Attribute) else a.id

    # Tuple
    if isinstance(ann, ast.Subscript) and ann.value.id == "Tuple":  # type: ignore
        al = []
        ind = 0
        for i in ann.slice.value.elts:  # type: ignore
            if isinstance(i, ast.Name) and to_name(i) == "bool":
                al.append((f"{base}.{ind}", to_name(i)))
            else:
                inner_list = translate_argument(i, base=f"{base}.{ind}")
                al.extend(inner_list)
            ind += 1
        return al

    # QintX
    elif to_name(ann)[0:4] == "Qint":
        n = int(to_name(ann)[4::])
        arg_list = [(f"{base}.{i}", "bool") for i in range(n)]
        # arg_list.append((f"{base}{arg.arg}", n))
        return arg_list

    # Bool
    elif to_name(ann) == "bool":
        return [(f"{base}", "bool")]

    else:
        raise exceptions.UnknownTypeException(ann)


def translate_arguments(args) -> Args:
    """Parse an argument list"""
    args_unrolled = map(
        lambda arg: translate_argument(arg.annotation, base=arg.arg), args
    )
    return utils.flatten(list(args_unrolled))


def translate_expression(expr, env: Env) -> BoolExp:  # noqa: C901
    """Translate an expression"""

    # Name reference
    if isinstance(expr, ast.Name):
        if Symbol(expr.id) not in env:
            raise exceptions.UnboundException(expr.id, env)
        return Symbol(expr.id)

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

        print(sn, ast.dump(expr))
        if Symbol(sn) not in env:
            raise exceptions.UnboundException(sn, env)
        return Symbol(sn)

    # Boolop: and, or
    elif isinstance(expr, ast.BoolOp):

        def unfold(v_exps, op):
            return (
                op(v_exps[0], unfold(v_exps[1::], op)) if len(v_exps) > 1 else v_exps[0]
            )

        v_exps = [translate_expression(e_in, env) for e_in in expr.values]

        return unfold(v_exps, And if isinstance(expr.op, ast.And) else Or)

    # Unary: not
    elif isinstance(expr, ast.UnaryOp):
        if isinstance(expr.op, ast.Not):
            return Not(translate_expression(expr.operand, env))
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # If expression
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

    # Constant
    elif isinstance(expr, ast.Constant):
        if expr.value is True:
            return true
        elif expr.value is False:
            return false
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # Tuple
    elif isinstance(expr, ast.Tuple):
        elts = [translate_expression(elt, env) for elt in expr.elts]
        return elts

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


def translate_statement(stmt, env: Env) -> Tuple[List[Tuple[str, BoolExp]], Env]:
    """Parse a statement"""
    # match stmt:
    if isinstance(stmt, ast.If):
        # Translate test expression, body & orelse statements
        # test = translate_expression(stmt.test, env)

        # body = []
        # for st_inner in stmt.body:
        #     exps, env = translate_statement(st_inner, env)
        #     body.extend(exps)

        # orelse = []
        # for st_inner in stmt.orelse:
        #     exps, env = translate_statement(st_inner, env)
        #     orelse.extend(exps)

        # print(ast.dump(stmt))
        raise exceptions.StatementNotHandledException(stmt)

    elif isinstance(stmt, ast.Assign):
        if len(stmt.targets) > 1:
            raise exceptions.StatementNotHandledException(
                stmt, f"too many targets {len(stmt.targets)}"
            )

        if not isinstance(stmt.targets[0], ast.Name):
            raise exceptions.StatementNotHandledException(
                stmt, "only name target supported"
            )

        target = Symbol(stmt.targets[0].id)

        if target in env:
            raise exceptions.SymbolReassingedException(target)

        val = translate_expression(stmt.value, env)

        # TODO: use translate argument here (or do a type inference)
        if isinstance(val, list):
            i = 0
            res = []
            for x in val:
                res.append((Symbol(f"{target}.{i}"), x))
                env[res[-1][0]] = "bool"
                i += 1
            return res, env
        else:
            env[target] = "bool"
            return [(target, val)], env

    elif isinstance(stmt, ast.Return):
        vexp = translate_expression(stmt.value, env)
        return [(Symbol("_ret"), vexp)], env

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
        env[Symbol(a_name)] = a_type

    if not fun.returns:
        raise exceptions.NoReturnTypeException()
    fun_ret: str = Symbol(fun.returns.id)
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
