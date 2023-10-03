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
from typing import List, Tuple

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from .. import exceptions
from ..typing import Env
from . import translate_expression, type_of_exp


def translate_statement(  # noqa: C901
    stmt, env: Env
) -> Tuple[List[Tuple[str, Boolean]], Env]:
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

        if target in env:
            raise exceptions.SymbolReassignedException(target)

        val = translate_expression(stmt.value, env)
        res, env = type_of_exp(val, f"{target}", env)
        res = list(map(lambda x: (Symbol(x[0]), x[1]), res))
        return res, env

    elif isinstance(stmt, ast.Return):
        vexp = translate_expression(stmt.value, env)
        res, env = type_of_exp(vexp, "_ret", env)
        res = list(map(lambda x: (Symbol(x[0]), x[1]), res))
        return res, env

        # FunctionDef
        # For
        # While
        # Expr
        # Pass
        # Break
        # Continue
        # Match

    else:
        raise exceptions.StatementNotHandledException(stmt)
