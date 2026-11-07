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

    tval, val = translate_expression(stmt.value, env)  # TODO: typecheck
    res = decompose_to_symbols(val, f"{target}")

    env.bind(Binding(target, tval, [x[0] for x in res]), rebind=target in env)
    res = list(map(lambda x: (Symbol(x[0]), x[1]), res))
    return res, env


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
    if isinstance(stmt, ast.If):  # This is handled by ast2ast
        raise exceptions.StatementNotHandledException(stmt)

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
