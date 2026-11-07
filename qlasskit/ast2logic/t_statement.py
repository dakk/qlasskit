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
import ast
from typing import List, Tuple
from uuid import uuid4

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from ..types import TType, TypeErrorException
from . import Binding, Env, decompose_to_symbols, exceptions, translate_expression


def __translate_assign(
    stmt: ast.Assign, env: Env
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    if len(stmt.targets) > 1:
        raise exceptions.StatementNotHandledException(
            stmt, f"too many targets {len(stmt.targets)}"
        )

    if not isinstance(stmt.targets[0], ast.Name):
        raise exceptions.StatementNotHandledException(
            stmt, "only name target supported"
        )

    target = stmt.targets[0].id

    # If self reference, use a temp var a -> __a = rhs; a = __a
    if target in env:
        tval, val = translate_expression(stmt.value, env)  # TODO: typecheck
        old_syms = {Symbol(b) for b in env[target].bitvec}
        # note: val may contain raw python bools (constant subscripts), which
        # have no free_symbols
        refs = (
            set().union(*[getattr(v, "free_symbols", set()) for v in val])
            if isinstance(val, list)
            else getattr(val, "free_symbols", set())
        )
        if refs & old_syms:
            tmp = f"__{target}"
            res = decompose_to_symbols(val, tmp)
            env.bind(Binding(tmp, tval, [x[0] for x in res]), rebind=tmp in env)
            exps: List[Tuple[str, Boolean]] = [(Symbol(n), e) for n, e in res]
            exps2, env = __translate_assign(
                ast.Assign(
                    targets=stmt.targets, value=ast.Name(id=tmp, ctx=ast.Load())
                ),
                env,
            )
            return exps + exps2, env

    tval, val = translate_expression(stmt.value, env)  # TODO: typecheck
    res = decompose_to_symbols(val, f"{target}")

    env.bind(Binding(target, tval, [x[0] for x in res]), rebind=target in env)
    res = list(map(lambda x: (Symbol(x[0]), x[1]), res))
    return res, env


def __translate_augassign(stmt: ast.AugAssign, env: Env):
    """Translate AugAssign (a += x) as Assign with a BinOp (a = a + x);
    the self-reference temp is handled by __translate_assign."""
    if not isinstance(stmt.target, ast.Name):
        raise exceptions.StatementNotHandledException(
            stmt, "only name target supported"
        )

    value = ast.BinOp(left=stmt.target, op=stmt.op, right=stmt.value)
    return __translate_assign(ast.Assign(targets=[stmt.target], value=value), env)




def __rewrite_if(stmt: ast.If, env: Env) -> List[ast.stmt]:
    """Rewrite if(c,t,e) into assigns with IfExp values, so: if c: d = x  else: d = y  becomes 
    _iftargN = c; d = x if _iftargN else d; d = d if _iftargN else y"""
    test_name = f"_iftarg{uuid4().hex}"

    def as_assign(b):
        if isinstance(b, ast.AugAssign) and isinstance(b.target, ast.Name):
            return ast.Assign(
                targets=[b.target],
                value=ast.BinOp(left=b.target, op=b.op, right=b.value),
            )
        return b

    def check_assign(b):
        if (
            not isinstance(b, ast.Assign)
            or len(b.targets) != 1
            or not isinstance(b.targets[0], ast.Name)
        ):
            raise exceptions.StatementNotHandledException(
                b, "if body only allows assigns"
            )
        return b.targets[0].id

    if_l: List[ast.stmt] = [
        ast.Assign(targets=[ast.Name(id=test_name, ctx=ast.Store())], value=stmt.test)
    ]

    for b in stmt.body:
        target = check_assign(as_assign(b))
        b = as_assign(b)
        orelse_inner = (
            ast.Name(id=target[2:], ctx=ast.Load())
            if target.startswith("__") and target not in env
            else ast.Name(id=target, ctx=ast.Load())
        )
        if_l.append(
            ast.Assign(
                targets=b.targets,
                value=ast.IfExp(
                    test=ast.Name(id=test_name, ctx=ast.Load()),
                    body=b.value,
                    orelse=orelse_inner,
                ),
            )
        )

    # flatten elif (nested If in orelse) by rewriting it first
    orelse: List[ast.stmt] = []
    for b in stmt.orelse:
        if isinstance(b, ast.If):
            orelse.extend(__rewrite_if(b, env))
        else:
            orelse.append(b)

    for b in orelse:
        b = as_assign(b)
        target = check_assign(b)
        if target.startswith("_iftarg"):
            if_l.append(b)
            continue
        orelse_inner = (
            ast.Name(id=target[2:], ctx=ast.Load())
            if target.startswith("__") and target not in env
            else ast.Name(id=target, ctx=ast.Load())
        )
        if_l.append(
            ast.Assign(
                targets=b.targets,
                value=ast.IfExp(
                    test=ast.Name(id=test_name, ctx=ast.Load()),
                    body=orelse_inner,
                    orelse=b.value,
                ),
            )
        )

    return if_l


def __translate_if(
    stmt: ast.If, env: Env, ret_type
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    """Translate if/else by rewriting it to straight-line IfExp assigns
    (see __rewrite_if) and translating those with the normal path."""
    exps: List[Tuple[str, Boolean]] = []
    for s in __rewrite_if(stmt, env):
        e, env = translate_statement(s, env, ret_type)
        exps.extend(e)
    return exps, env


def __translate_return(
    stmt: ast.Return, env: Env, ret_type
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    texp, vexp = translate_expression(stmt.value, env)  # TODO: typecheck

    if (
        hasattr(texp, "BIT_SIZE")
        and hasattr(ret_type, "BIT_SIZE")
        and texp.BIT_SIZE < ret_type.BIT_SIZE
    ):
        texp, vexp = ret_type.fill((texp, vexp))  # type: ignore
    elif (
        hasattr(texp, "BIT_SIZE")
        and hasattr(ret_type, "BIT_SIZE")
        and texp.BIT_SIZE > ret_type.BIT_SIZE
    ):
        texp, vexp = ret_type.crop((texp, vexp))  # type: ignore
    elif texp != ret_type:
        raise TypeErrorException(texp, ret_type)

    res = decompose_to_symbols(vexp, "_ret")
    env.bind(Binding("_ret", texp, [x[0] for x in res]))
    res = list(map(lambda x: (Symbol(x[0]), x[1]), res))
    return res, env


def __translate_functiondef(
    stmt: ast.FunctionDef, env: Env
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    from .t_ast import translate_ast

    lofun = translate_ast(stmt)
    env.bind_function(lofun)
    return [], env


def translate_statement(  # noqa: C901
    stmt, env: Env, ret_type: TType
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    """Parse a statement"""
    # match stmt:
    if isinstance(stmt, ast.If):
        return __translate_if(stmt, env, ret_type)

    elif isinstance(stmt, ast.AugAssign):
        return __translate_augassign(stmt, env)

    elif isinstance(stmt, ast.Assign):
        return __translate_assign(stmt, env)

    elif isinstance(stmt, ast.Return):
        return __translate_return(stmt, env, ret_type)

    elif isinstance(stmt, ast.FunctionDef):
        return __translate_functiondef(stmt, env)

    elif isinstance(stmt, ast.Expr):
        if hasattr(stmt, "value"):
            texp, vexp = translate_expression(stmt.value, env)
        return [], env

        # While
        # Expr
        # Pass
        # Break
        # Continue
        # Match

    else:
        raise exceptions.StatementNotHandledException(stmt)
