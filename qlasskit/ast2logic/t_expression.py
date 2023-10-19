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
from typing import List, Tuple, get_args

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or, false, true

from ..types import Qbool, Qtype, TExp, const_to_qtype
from . import Env, exceptions


def decompose_to_symbols(vlist, base, res=[]) -> List[Symbol]:
    """Decompose exp to symbols"""
    if isinstance(vlist, list):
        i = 0
        res = []
        for in_val in vlist:
            r_new = decompose_to_symbols(in_val, f"{base}.{i}", res)
            if isinstance(r_new, list):
                res.extend(r_new)
            else:
                res.append(r_new)
            i += 1
        return res
    else:
        new_symb = (f"{base}", vlist)
        return [new_symb]


def translate_expression(expr, env: Env) -> TExp:  # noqa: C901
    """Translate an expression"""

    # Name reference
    if isinstance(expr, ast.Name):
        binding = env[expr.id]
        return (binding.ttype, binding.to_exp())

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

        if sn.split(".")[0] not in env:
            raise exceptions.UnboundException(sn, env)

        # Get the inner type
        inner_type = env[sn.split(".")[0]].ttype
        for i in sn.split(".")[1:]:
            if hasattr(inner_type, "BIT_SIZE"):
                if int(i) < inner_type.BIT_SIZE:
                    inner_type = bool
                else:
                    raise exceptions.OutOfBoundException(inner_type.BIT_SIZE, i)
            else:
                if int(i) < len(get_args(inner_type)):
                    inner_type = get_args(inner_type)[int(i)]
                else:
                    raise exceptions.OutOfBoundException(len(get_args(inner_type)), i)

        if hasattr(inner_type, "BIT_SIZE"):
            return (
                inner_type,
                [Symbol(f"{sn}.{i}") for i in range(inner_type.BIT_SIZE)],
            )
        else:
            return (inner_type, Symbol(sn))

    # Boolop: and, or
    elif isinstance(expr, ast.BoolOp):

        def unfold(v_exps, op):
            return (
                op(v_exps[0], unfold(v_exps[1::], op)) if len(v_exps) > 1 else v_exps[0]
            )

        vt_exps = [translate_expression(e_in, env) for e_in in expr.values]
        v_exps = [x[1] for x in vt_exps]
        for x in vt_exps:
            if x[0] != bool:
                raise exceptions.TypeErrorException(x[0], bool)

        return (bool, unfold(v_exps, And if isinstance(expr.op, ast.And) else Or))

    # Unary: not
    elif isinstance(expr, ast.UnaryOp):
        if isinstance(expr.op, ast.Not):
            texp, exp = translate_expression(expr.operand, env)

            if texp != bool:
                raise exceptions.TypeErrorException(texp, bool)

            return (bool, Not(exp))
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # If expression
    elif isinstance(expr, ast.IfExp):
        te_test = translate_expression(expr.test, env)
        te_true = translate_expression(expr.body, env)
        te_false = translate_expression(expr.orelse, env)

        if te_test[0] != bool:
            raise exceptions.TypeErrorException(te_test[0], bool)

        if te_true[0] != te_false[0]:
            raise exceptions.TypeErrorException(te_false[0], te_true[0])

        if te_true[0] == bool:
            return (
                te_true[0],
                ITE(te_test[1], te_true[1], te_false[1]),
            )
        else:
            return (
                te_true[0],
                [ITE(te_test[1], t, f) for t, f in zip(te_true[1], te_false[1])],
            )

    # Constant
    elif isinstance(expr, ast.Constant):
        if expr.value is True:
            return (bool, true)
        elif expr.value is False:
            return (bool, false)

        q_value = const_to_qtype(expr.value)

        if q_value:
            return q_value
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # Tuple
    elif isinstance(expr, ast.Tuple):
        telts = [translate_expression(elt, env) for elt in expr.elts]
        elts = [x[1] for x in telts]
        tlts = [x[0] for x in telts]

        return (Tuple[tuple(tlts)], elts)

    # Compare operator
    elif isinstance(expr, ast.Compare):
        if len(expr.ops) != 1 or len(expr.comparators) != 1:
            raise exceptions.ExpressionNotHandledException(expr)

        tleft = translate_expression(expr.left, env)
        tcomp = translate_expression(expr.comparators[0], env)

        # Check comparability
        if tleft[0] == bool and tcomp[0] == bool:
            op_type = Qbool
        elif issubclass(tleft[0], Qtype) and issubclass(tcomp[0], Qtype):  # type: ignore
            if not tleft[0].comparable(tcomp[0]):  # type: ignore
                raise exceptions.TypeErrorException(tcomp[0], tleft[0])
            op_type = tleft[0]  # type: ignore

        # Call the comparator
        comparators = [
            (ast.Eq, "eq"),
            (ast.NotEq, "neq"),
            (ast.Lt, "lt"),
            (ast.LtE, "lte"),
            (ast.Gt, "gt"),
            (ast.GtE, "gte"),
        ]

        for ast_comp, comp_name in comparators:
            if isinstance(expr.ops[0], ast_comp):
                if not hasattr(op_type, comp_name):
                    raise exceptions.OperationNotSupportedException(op_type, comp_name)

                return getattr(op_type, comp_name)(tleft, tcomp)

        # Is | IsNot | In | NotIn
        raise exceptions.ExpressionNotHandledException(expr)

    # Binop
    elif isinstance(expr, ast.BinOp):
        # Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift | RShift
        # | BitOr | BitXor | BitAnd | FloorDiv
        # print(ast.dump(expr))
        tleft = translate_expression(expr.left, env)
        tright = translate_expression(expr.right, env)

        if isinstance(expr.op, ast.Add) and hasattr(tleft[0], "add"):
            return tleft[0].add(tleft, tright)
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # Call
    elif isinstance(expr, ast.Call):
        if not hasattr(expr.func, "id"):
            raise exceptions.ExpressionNotHandledException(expr)

        # Typecast
        if (
            env.know_type(expr.func.id)
            and len(expr.args) == 1
            and isinstance(expr.args[0], ast.Constant)
        ):
            return env.gettype(expr.func.id).const(expr.args[0].value)

        raise exceptions.ExpressionNotHandledException(expr)

    # Lambda
    # Dict
    # Set
    # Call
    # List

    else:
        raise exceptions.ExpressionNotHandledException(expr)
