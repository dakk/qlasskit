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
from typing import List, Tuple, get_args

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or, Xor, false, true

from ..boolquant import QuantumBooleanGate
from ..types import Qbool, Qfixed, Qint, Qtype, TExp, TypeErrorException, const_to_qtype
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

        def unroll_subscripts(sub: ast.Subscript, st):
            _sval = sub.slice

            if isinstance(sub.value, ast.Subscript):
                st = f"{_sval.value}{'.' if st else ''}{st}"  # type: ignore
                return unroll_subscripts(sub.value, st)
            elif isinstance(sub.value, ast.Name):
                return f"{sub.value.id}.{_sval.value}.{st}"  # type: ignore
            elif (
                isinstance(sub.value, ast.Constant)
                and hasattr(sub.value.value, "elts")
                and isinstance(sub.slice, ast.Constant)
            ):
                return sub.value.value.elts[sub.slice.value]
            else:
                raise Exception(f"Subscript not handled: {ast.dump(sub)} {st}")

        _sval = expr.slice  # type: ignore

        if not isinstance(_sval, ast.Constant):
            raise exceptions.ExpressionNotHandledException(expr)

        if isinstance(expr.value, ast.Name):
            sn = f"{expr.value.id}.{_sval.value}"
        else:
            sn = unroll_subscripts(expr, "")

        if isinstance(sn, ast.Constant):
            return (bool, sn.value)

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
                raise TypeErrorException(x[0], bool)

        return (bool, unfold(v_exps, And if isinstance(expr.op, ast.And) else Or))

    # Unary: not
    elif isinstance(expr, ast.UnaryOp):
        texp, exp = translate_expression(expr.operand, env)

        if isinstance(expr.op, ast.Not):
            if texp != bool:
                raise TypeErrorException(texp, bool)
            return (bool, Not(exp))

        elif isinstance(expr.op, ast.Invert) and hasattr(texp, "bitwise_not"):
            return texp.bitwise_not((texp, exp))
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # If expression
    elif isinstance(expr, ast.IfExp):
        te_test = translate_expression(expr.test, env)
        te_true = translate_expression(expr.body, env)
        te_false = translate_expression(expr.orelse, env)

        if te_test[0] != bool:
            raise TypeErrorException(te_test[0], bool)

        if te_true[0] != te_false[0]:
            if not hasattr(te_true[0], "BIT_SIZE") or not hasattr(
                te_false[0], "BIT_SIZE"
            ):
                raise TypeErrorException(te_false[0], te_true[0])

            if te_true[0].BIT_SIZE > te_false[0].BIT_SIZE:
                te_false = te_true[0].fill(te_false)  # type: ignore
            elif te_true[0].BIT_SIZE < te_false[0].BIT_SIZE:  # type: ignore
                te_true = te_false[0].fill(te_true)  # type: ignore

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
        elif isinstance(expr.value, ast.Tuple):
            types = []
            values = []
            for x in expr.value.elts:  # type: ignore
                t, e = const_to_qtype(x.value)  # type: ignore
                types.append(t)
                values.append(e)
            return (Tuple[tuple(types)], values)  # type: ignore

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

        return (Tuple[tuple(tlts)], elts)  # type: ignore

    # Compare operator
    elif isinstance(expr, ast.Compare):
        if len(expr.ops) != 1 or len(expr.comparators) != 1:
            raise exceptions.ExpressionNotHandledException(expr)

        tleft = translate_expression(expr.left, env)
        tcomp = translate_expression(expr.comparators[0], env)

        # Check comparability
        if tleft[0] == bool and tcomp[0] == bool:
            op_type = Qbool

        # Compare tuples for equality / inequality
        elif len(get_args(tleft[0])) > 0 and len(get_args(tcomp[0])) > 0:
            arg_l = get_args(tleft[0])
            arg_r = get_args(tcomp[0])
            if arg_l != arg_r:
                raise TypeErrorException(tleft[0], tcomp[0])

            if isinstance(expr.ops[0], ast.Eq):
                op = Qbool.eq
            elif isinstance(expr.ops[0], ast.NotEq):
                op = Qbool.neq
            else:
                raise exceptions.OperationNotSupportedException(bool, expr.ops[0])

            c = True
            idx = 0
            for left, right in zip(arg_l, arg_r):
                if left == bool:
                    c = And(c, op((bool, tleft[1][idx]), (bool, tcomp[1][idx]))[1])
                    idx += 1
                else:
                    for si in range(left.BIT_SIZE):
                        c = And(c, op((bool, tleft[1][idx]), (bool, tcomp[1][idx]))[1])
                        idx += 1

            return (bool, c)

        elif issubclass(tleft[0], Qtype) and issubclass(tcomp[0], Qtype):  # type: ignore
            if not tleft[0].comparable(tcomp[0]):  # type: ignore
                raise TypeErrorException(tcomp[0], tleft[0])
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
        # Sub | Mult | MatMult | Div | Mod | Pow | FloorDiv
        # print(ast.dump(expr))
        tleft = translate_expression(expr.left, env)
        tright = translate_expression(expr.right, env)

        if tleft[0] == bool and tright[0] == bool:
            if isinstance(expr.op, ast.BitXor):
                return bool, Xor(tleft[1], tright[1])
            elif isinstance(expr.op, ast.BitAnd):
                return bool, And(tleft[1], tright[1])
            elif isinstance(expr.op, ast.BitOr):
                return bool, Or(tleft[1], tright[1])

        if isinstance(expr.op, ast.Add) and hasattr(tleft[0], "add"):
            return tleft[0].add(tleft, tright)
        elif isinstance(expr.op, ast.Sub) and hasattr(tleft[0], "sub"):
            return tleft[0].sub(tleft, tright)
        elif isinstance(expr.op, ast.Mult) and hasattr(tleft[0], "mul"):
            return tleft[0].mul(tleft, tright)
        elif isinstance(expr.op, ast.Mod):
            return tleft[0].mod(tleft, tright)  # type: ignore
        elif isinstance(expr.op, ast.BitXor) and hasattr(tleft[0], "bitwise_xor"):
            return tleft[0].bitwise_xor(tleft, tright)
        elif isinstance(expr.op, ast.BitAnd) and hasattr(tleft[0], "bitwise_and"):
            return tright[0].bitwise_and(tleft, tright)  # type: ignore
        elif isinstance(expr.op, ast.BitOr) and hasattr(tleft[0], "bitwise_or"):
            return tleft[0].bitwise_or(tleft, tright)
        elif (
            isinstance(expr.op, ast.LShift)
            and hasattr(tleft[0], "shift_left")
            and isinstance(expr.right, ast.Constant)
        ):
            return tleft[0].shift_left(tleft, expr.right.value)
        elif (
            isinstance(expr.op, ast.RShift)
            and hasattr(tleft[0], "shift_right")
            and isinstance(expr.right, ast.Constant)
        ):
            return tleft[0].shift_right(tleft, expr.right.value)
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # Call
    elif isinstance(expr, ast.Call):
        # Quantum hybrid
        if (
            isinstance(expr.func, ast.Attribute)
            and isinstance(expr.func.value, ast.Name)
            and expr.func.value.id == "Q"
        ):
            gate = expr.func.attr
            args = [translate_expression(e, env) for e in expr.args]
            args_v = [b for (a, b) in args]

            q_gate = QuantumBooleanGate.build(gate)

            if len(args_v) == 1 and isinstance(args_v[0], list):
                return args[0][0], [q_gate(a) for a in args_v[0]]
            else:
                return args[0][0], q_gate(*args_v)

        elif not hasattr(expr.func, "id"):
            raise exceptions.ExpressionNotHandledException(expr)

        # Typecast
        elif env.know_type(expr.func.id):
            if len(expr.args) != 1:
                raise Exception(
                    f"{expr.func.id}() takes exactly 1 argument ({len(expr.args)} given)"
                )

            if not isinstance(expr.args[0], ast.Constant):
                raise Exception(f"{expr.func.id}() accepts only constant values")

            return env.gettype(expr.func.id).const(expr.args[0].value)

        # int()
        elif expr.func.id == "int":
            if len(expr.args) != 1:
                raise Exception(
                    f"int() takes exactly 1 argument ({len(expr.args)} given)"
                )

            (ta, te) = translate_expression(expr.args[0], env)
            if ta.__name__[:4] == "Qint":
                return (ta, te)
            elif ta.__name__[:6] == "Qfixed":
                ip = ta.integer_part((ta, te))  # type: ignore
                return (Qint.type_for_size(len(ip)), ip)
            else:
                raise Exception(f"int() accepts only Qfixed and Qint: {ta} given")

        # float()
        elif expr.func.id == "float":
            if len(expr.args) != 1:
                raise Exception(
                    f"float() takes exactly 1 argument ({len(expr.args)} given)"
                )

            (ta, te) = translate_expression(expr.args[0], env)
            if ta.__name__[:6] == "Qfixed":
                return (ta, te)
            elif ta.__name__[:4] == "Qint":
                tf = Qfixed.type_for_size(len(te))
                return tf.fill((tf, te))
            else:
                raise Exception(f"float() accepts only Qfixed and Qint: {ta} given")

        # Known function
        elif env.know_function(expr.func.id):
            def_f = env.getdef(expr.func.id)
            args = [translate_expression(e, env) for e in expr.args]

            # Check if args match function args and replace
            if len(args) != len(def_f[1]):
                raise TypeErrorException(args, def_f[1])

            subs = {}
            for a, fa in zip(args, def_f[1]):
                if isinstance(a[1], List):
                    for i in range(len(a[1])):  # type: ignore
                        index = ".".join(a[1][i].name.split(".")[1:])  # type: ignore
                        if index == "":
                            index = f"{i}"

                        subs[f"{fa.name}.{index}"] = a[1][i]  # type: ignore

                else:
                    subs[fa.name] = a[1]

            n_exps = []
            for s, e in def_f[3]:
                n_exps.append((s, e.subs(subs, simultaneus=True)))

            _ret = list(map(lambda se: se[1], n_exps))

            if len(_ret) == 1:
                return (bool, _ret[0])

            return (def_f[2].ttype, _ret)

        raise exceptions.UnknownSymbolException(expr.func.id, env)

    # Lambda
    # Dict
    # Set

    else:
        raise exceptions.ExpressionNotHandledException(expr)
