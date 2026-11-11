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
import copy
from typing import Any, List, Tuple, get_args
from uuid import uuid4

from sympy import Symbol
from sympy.logic.boolalg import Boolean

from ..types import TType, TypeErrorException
from . import (
    Binding,
    Env,
    decompose_to_symbols,
    exceptions,
    flatten,
    translate_expression,
)


def _py_to_ast(v) -> ast.expr:
    """Convert a python constant (scalar/list/tuple) to an AST literal"""
    if isinstance(v, (list, tuple)):
        return ast.Tuple(elts=[_py_to_ast(x) for x in v])
    return ast.Constant(value=v)


class NameValReplacer(ast.NodeTransformer):
    """Replace all Name with name_id with the given val"""

    def __init__(self, name_id: str, val: Any):
        self.name_id = name_id
        self.val = val

    def visit_Name(self, node):
        if node.id == self.name_id:
            return self.val
        return node


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

    # track python constants for constant-subscript unrolling
    try:
        env.set_constant(target, ast.literal_eval(stmt.value))
    except Exception:
        env.remove_constant(target)

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


def __translate_augassign(
    stmt: ast.AugAssign, env: Env
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    """Translate a += x to a = a + x"""
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

    # unroll nested for/if in the body first
    body: List[ast.stmt] = []
    for b in stmt.body:
        body.extend(__unroll_stmt(b, env))

    for b in body:
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

    # flatten nested for/if in orelse (elif) by unrolling/rewriting first
    orelse: List[ast.stmt] = []
    for b in stmt.orelse:
        orelse.extend(__unroll_stmt(b, env))

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
    (see __rewrite_if) and translating those with the normal path"""
    exps: List[Tuple[str, Boolean]] = []
    for s in __rewrite_if(stmt, env):
        e, env = translate_statement(s, env, ret_type)
        exps.extend(e)
    return exps, env


def __unroll_arg(arg, env: Env) -> List:
    """Transform a for-loop iterable to a list: Tuple literals, constants,
    tuple-typed names (a -> a[0], a[1], ...) and tuple subscripts (a[k] ->
    a[k][0], ...)"""
    if isinstance(arg, ast.Tuple):
        return arg.elts
    if isinstance(arg, ast.Constant) and isinstance(arg.value, ast.Tuple):
        return arg.value.elts
    if isinstance(arg, ast.Name) and arg.id in env and env.has_constant(arg.id):
        v = env.get_constant(arg.id)
        vals = list(v) if isinstance(v, (list, tuple)) else [v]
        return [_py_to_ast(x) for x in vals]
    if isinstance(arg, ast.Name) and arg.id in env:
        t = env[arg.id].ttype
        if not hasattr(t, "BIT_SIZE") and get_args(t):
            return [
                ast.Subscript(
                    value=ast.Name(id=arg.id, ctx=ast.Load()),
                    slice=ast.Constant(value=i),
                    ctx=ast.Load(),
                )
                for i in range(len(get_args(t)))
            ]
    if (
        isinstance(arg, ast.Subscript)
        and isinstance(arg.value, ast.Name)
        and arg.value.id in env
        and isinstance(arg.slice, ast.Constant)
    ):
        t = env[arg.value.id].ttype
        if not hasattr(t, "BIT_SIZE") and get_args(t):
            inner = get_args(t)[arg.slice.value]  # type: ignore
            n = (
                len(get_args(inner))
                if get_args(inner)
                else getattr(inner, "BIT_SIZE", 1)
            )
            return [
                ast.Subscript(
                    value=ast.Subscript(
                        value=ast.Name(id=arg.value.id, ctx=ast.Load()),
                        slice=ast.Constant(value=arg.slice.value),
                        ctx=ast.Load(),
                    ),
                    slice=ast.Constant(value=i),
                    ctx=ast.Load(),
                )
                for i in range(n)
            ]
    return [arg]


def __unroll_for(stmt: ast.For, env: Env) -> List[ast.stmt]:
    """Unroll a for loop into straight-line statements: per iteration,
    assign the loop var to its constant value, then the body with the
    loop var replaced by that constant"""
    if not isinstance(stmt.target, ast.Name):
        raise exceptions.StatementNotHandledException(
            stmt, "only name target supported"
        )

    it = stmt.iter
    if (
        isinstance(it, ast.Call)
        and isinstance(it.func, ast.Name)
        and it.func.id == "range"
    ):
        args = [ast.literal_eval(a) for a in it.args]
        it_vals: List = list(range(*args))
    else:
        it_vals = flatten(__unroll_arg(it, env))

    rolls: List[ast.stmt] = []
    for i in it_vals:
        _val = (
            i if isinstance(i, (ast.Constant, ast.Subscript)) else ast.Constant(value=i)
        )
        rolls.append(ast.Assign(targets=[stmt.target], value=_val))
        for b in stmt.body:
            rolls.append(NameValReplacer(stmt.target.id, _val).visit(copy.deepcopy(b)))
    return rolls


def __unroll_stmt(stmt, env: Env) -> List[ast.stmt]:
    """Unroll for/if statements into straight-line statements."""
    if isinstance(stmt, ast.For):
        return __unroll_for(stmt, env)
    if isinstance(stmt, ast.If):
        return __rewrite_if(stmt, env)
    return [stmt]


def __translate_for(
    stmt: ast.For, env: Env, ret_type
) -> Tuple[List[Tuple[str, Boolean]], Env]:
    exps: List[Tuple[str, Boolean]] = []
    for s in __unroll_for(stmt, env):
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

    elif isinstance(stmt, ast.For):
        return __translate_for(stmt, env, ret_type)

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
