# Copyright 2023-2024 Davide Gessa

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
from typing import List, Tuple

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from ..types import TType, TypeErrorException
from . import Binding, Env, decompose_to_symbols, exceptions, translate_expression


def translate_statement(  # noqa: C901
    stmt, env: Env, ret_type: TType
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    """Parse a statement"""
    # match stmt:
    if isinstance(stmt, ast.If):  # This is handled by ast2ast
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

        target = stmt.targets[0].id

        tval, val = translate_expression(stmt.value, env)  # TODO: typecheck
        res = decompose_to_symbols(val, f"{target}")

        env.bind(Binding(target, tval, [x[0] for x in res]), rebind=target in env)
        res = list(map(lambda x: (Symbol(x[0]), x[1]), res))
        return res, env

    elif isinstance(stmt, ast.Return):
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

    elif isinstance(stmt, ast.FunctionDef):
        from .t_ast import translate_ast

        lofun = translate_ast(stmt)
        env.bind_function(lofun)
        return [], env

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
