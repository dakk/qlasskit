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
from typing import List, Tuple, cast, get_args

from sympy import Symbol
from sympy.logic import ITE, And, Not, Or, Xor, false, true

from ..boolquant import QuantumBooleanGate
from ..types import Qbool, Qfixed, Qint, Qtype, TExp, TypeErrorException, const_to_qtype
from . import Env, exceptions
from .utils import safe_str


def decompose_to_symbols(vlist, base, res: List = []) -> List[Symbol]:
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


class ExpressionTranslator(ast.NodeTransformer):
    def __init__(self, env: Env):
        self.env = env
        self.__call_dispatch = {
            "range": self.__call_range,
            "len": self.__call_len,
            "sum": self.__call_sum,
            "ord": self.__call_ord,
            "chr": self.__call_chr,
            "any": self.__call_anyall,
            "all": self.__call_anyall,
            "min": self.__call_minmax,
            "max": self.__call_minmax,
        }

        self.__binop_dispatch = {
            ast.Add: "add",
            ast.Sub: "sub",
            ast.Mult: "mul",
            ast.Mod: "mod",
            ast.FloorDiv: "floor_div",
            ast.BitXor: "bitwise_xor",
            ast.BitAnd: "bitwise_and",
            ast.BitOr: "bitwise_or",
        }

    # Name reference
    def visit_Name(self, expr: ast.Name):
        # __ prefix is reserved for internal use
        if expr.id.startswith("__") and expr.id not in self.env:
            raise Exception("invalid name starting with __")

        binding = self.env[expr.id]
        return (binding.ttype, binding.to_exp())

    @staticmethod
    def __py_to_ast(v) -> ast.expr:
        if isinstance(v, (list, tuple)):
            return ast.List(elts=[ExpressionTranslator.__py_to_ast(x) for x in v])
        return ast.Constant(value=v)

    def __const_chain(self, node, slices) -> ast.expr:
        """Build an IfExp chain over a constant: for slices (innermost
        first), constant slices navigate the value, the first dynamic slice
        becomes an IfExp(i == k, elem_k, ...) chain"""
        if not slices:
            return self.__py_to_ast(node)
        s, rest = slices[0], slices[1:]
        if isinstance(s, ast.Constant):
            return self.__const_chain(node[s.value], rest)
        n = len(node)
        chain = self.__const_chain(node[n - 1], rest)
        for k in reversed(range(n - 1)):
            chain = ast.IfExp(
                test=ast.Compare(
                    left=copy.deepcopy(s),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=k)],
                ),
                body=self.__const_chain(node[k], rest),
                orelse=chain,
            )
        return chain

    @staticmethod
    def __first_dim(ttype) -> int:
        """First dimension of a type: BIT_SIZE for Qint-like, len(args) for Tuple"""
        if hasattr(ttype, "BIT_SIZE"):
            return ttype.BIT_SIZE  # type: ignore
        args = get_args(ttype)
        return len(args) if args else 1

    def __dyn_subscript_chain(self, expr: ast.Subscript) -> ast.IfExp:
        """L[0] if i==0 else L[1] if i==1 ... else L[max] for a var idx (L[max] fallthrough)"""
        if isinstance(expr.value, ast.Name):
            vt = self.env[expr.value.id].ttype
        else:
            # nested subscript (m[i][j]): type of the subscripted value (the row)
            vt = self.visit(expr.value)[0]
        n = self.__first_dim(vt)

        def access(k) -> ast.Subscript:
            return ast.Subscript(
                value=expr.value, slice=ast.Constant(value=k), ctx=ast.Load()
            )

        chain: ast.IfExp | ast.Subscript = access(n - 1)
        for k in reversed(range(n - 1)):
            chain = ast.IfExp(
                test=ast.Compare(
                    left=copy.deepcopy(expr.slice),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=k)],
                ),
                body=access(k),
                orelse=chain,
            )
        return chain  # type: ignore

    # Subscript: a[0][1]
    def visit_Subscript(self, expr: ast.Subscript):  # noqa: C901
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
                return sub.value.value.elts[sub.slice.value]  # type: ignore
            else:
                raise Exception(f"Subscript not handled: {ast.dump(sub)} {st}")

        _sval = expr.slice  # type: ignore

        # if the base of the subscript chain is a constant, unroll
        base = expr.value
        slices = []
        while isinstance(base, ast.Subscript):
            slices.append(base.slice)
            base = base.value
        slices.append(expr.slice)
        slices.reverse()  # innermost first
        if isinstance(base, ast.Name) and self.env.has_constant(base.id):
            return self.visit(
                self.__const_chain(self.env.get_constant(base.id), slices)
            )

        if not isinstance(_sval, ast.Constant):
            # variable index: build L[0] if i==0 else L[1] if ... else L[max] as an IfExp
            # chain, sized from the base type's first dimension, then translate it
            return self.visit(self.__dyn_subscript_chain(expr))

        if isinstance(expr.value, ast.Subscript) and not isinstance(
            expr.value.slice, ast.Constant
        ):
            # constant outer slice over a dynamic inner subscript (t[i][0]):
            # translate the inner subscript first, then index into the result
            vt, vexp = self.visit(expr.value)
            if isinstance(vexp, list):
                args = get_args(vt)
                if args and _sval.value < len(args):  # type: ignore
                    etype = args[_sval.value]  # type: ignore
                else:
                    etype = bool
                esize = etype.BIT_SIZE if hasattr(etype, "BIT_SIZE") else 1
                elem = vexp[_sval.value * esize : (_sval.value + 1) * esize]  # type: ignore
                return (etype, elem if esize > 1 else elem[0])
            raise exceptions.ExpressionNotHandledException(expr)

        if isinstance(expr.value, (ast.Tuple, ast.List)):
            # constant tuple/list literal subscript: pick the element directly
            return self.visit(expr.value.elts[_sval.value])  # type: ignore

        if isinstance(expr.value, ast.Name):
            sn = f"{expr.value.id}.{safe_str(_sval.value)}"
        else:
            sn = unroll_subscripts(expr, "")

        if isinstance(sn, ast.Constant):
            return (bool, sn.value)

        if sn.split(".")[0] not in self.env:
            raise exceptions.UnboundException(sn, self.env)

        # Get the inner type
        inner_type = self.env[sn.split(".")[0]].ttype
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
        elif inner_type == bool:
            return (bool, Symbol(sn))
        else:
            # tuple element: collect its bits from the base binding's bitvec
            bits = [
                b for b in self.env[sn.split(".")[0]].bitvec if b.startswith(sn + ".")
            ]
            return (inner_type, [Symbol(b) for b in bits])

    # Boolop: and, or
    def visit_BoolOp(self, expr: ast.BoolOp):
        def unfold(v_exps, op):
            return (
                op(v_exps[0], unfold(v_exps[1::], op)) if len(v_exps) > 1 else v_exps[0]
            )

        vt_exps = [self.visit(e_in) for e_in in expr.values]
        v_exps = [x[1] for x in vt_exps]
        for x in vt_exps:
            if x[0] != bool:
                raise TypeErrorException(x[0], bool)

        return (bool, unfold(v_exps, And if isinstance(expr.op, ast.And) else Or))

    # Unary: not
    def visit_UnaryOp(self, expr: ast.UnaryOp):
        texp, exp = self.visit(expr.operand)

        if isinstance(expr.op, ast.Not):
            if texp != bool:
                raise TypeErrorException(texp, bool)
            return (bool, Not(exp))

        elif isinstance(expr.op, ast.Invert) and hasattr(texp, "bitwise_not"):
            return texp.bitwise_not((texp, exp))
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    # If expression
    def visit_IfExp(self, expr: ast.IfExp):
        te_test = self.visit(expr.test)
        te_true = self.visit(expr.body)
        te_false = self.visit(expr.orelse)

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
    def visit_Constant(self, expr: ast.Constant):
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
    def visit_Tuple(self, expr: ast.Tuple):
        telts = [self.visit(elt) for elt in expr.elts]
        elts = [x[1] for x in telts]
        tlts = [x[0] for x in telts]

        return (Tuple[tuple(tlts)], elts)  # type: ignore

    # List
    def visit_List(self, node: ast.List):
        """Converts List to Tuple"""
        return self.visit_Tuple(ast.Tuple(elts=node.elts, ctx=node.ctx))

    # Compare operator
    def visit_Compare(self, expr: ast.Compare):  # noqa: C901
        if len(expr.ops) != 1 or len(expr.comparators) != 1:
            raise exceptions.ExpressionNotHandledException(expr)

        tleft = self.visit(expr.left)
        tcomp = self.visit(expr.comparators[0])

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

                return getattr(op_type, comp_name)(tleft, tcomp)  # type: ignore

        # Is | IsNot | In | NotIn
        raise exceptions.ExpressionNotHandledException(expr)

    # Binop
    def visit_BinOp(self, expr: ast.BinOp):  # noqa: C901
        # Sub | Mult | MatMult | Div | Mod | Pow | FloorDiv | Xor | And | Or
        tleft = self.visit(expr.left)
        tright = self.visit(expr.right)

        if tleft[0] == bool and tright[0] == bool:
            if isinstance(expr.op, ast.BitXor):
                return bool, Xor(tleft[1], tright[1])
            elif isinstance(expr.op, ast.BitAnd):
                return bool, And(tleft[1], tright[1])
            elif isinstance(expr.op, ast.BitOr):
                return bool, Or(tleft[1], tright[1])

        if isinstance(expr.op, ast.Pow) and hasattr(tleft[0], "mul"):
            # Transform pow to multiplications
            if not isinstance(expr.right, ast.Constant) and not isinstance(
                expr.right.value, int  # type: ignore
            ):
                raise exceptions.ExpressionNotHandledException(expr.right)

            if expr.right.value > 0:  # type: ignore
                result = tleft
                for _ in range(expr.right.value - 1):  # type: ignore
                    result = result[0].mul(result, tleft)

                return result
            elif expr.right.value == 0:  # type: ignore
                return const_to_qtype(1)
            else:
                raise exceptions.ExpressionNotHandledException(expr.right)
        elif (
            isinstance(expr.op, ast.LShift)
            and hasattr(tleft[0], "shift_left")
            and isinstance(expr.right, ast.Constant)
        ):
            return tleft[0].shift_left(tleft, expr.right.value)  # type: ignore
        elif (
            isinstance(expr.op, ast.RShift)
            and hasattr(tleft[0], "shift_right")
            and isinstance(expr.right, ast.Constant)
        ):
            return tleft[0].shift_right(tleft, expr.right.value)  # type: ignore
        else:
            mt = self.__binop_dispatch.get(type(expr.op))

            if mt is not None and hasattr(tleft[0], mt):
                return getattr(tleft[0], mt)(tleft, tright)
            else:
                raise exceptions.ExpressionNotHandledException(expr)

    def __unroll_arg(self, arg) -> List:
        """Translate a call argument to a list of TExp (tuple/list literal,
        constant, tuple-typed name or tuple subscript)"""
        if isinstance(arg, (ast.Tuple, ast.List)):
            return [self.visit(el) for el in arg.elts]
        if isinstance(arg, ast.Name) and arg.id in self.env:
            if self.env.has_constant(arg.id):
                v = self.env.get_constant(arg.id)
                vals = list(v) if isinstance(v, (list, tuple)) else [v]
                return [self.visit(self.__py_to_ast(x)) for x in vals]
            t = self.env[arg.id].ttype
            if not hasattr(t, "BIT_SIZE") and get_args(t):
                return [
                    self.visit(
                        ast.Subscript(
                            value=arg, slice=ast.Constant(value=i), ctx=ast.Load()
                        )
                    )
                    for i in range(len(get_args(t)))
                ]
        if (
            isinstance(arg, ast.Subscript)
            and isinstance(arg.value, ast.Name)
            and isinstance(arg.slice, ast.Constant)
            and arg.value.id in self.env
        ):
            t = self.env[arg.value.id].ttype
            if not hasattr(t, "BIT_SIZE") and get_args(t):
                inner = get_args(t)[arg.slice.value]  # type: ignore
                n = (
                    len(get_args(inner))
                    if get_args(inner)
                    else getattr(inner, "BIT_SIZE", 1)
                )
                return [
                    self.visit(
                        ast.Subscript(
                            value=arg, slice=ast.Constant(value=i), ctx=ast.Load()
                        )
                    )
                    for i in range(n)
                ]
        return [self.visit(arg)]

    def __call_range(self, node: ast.Call):
        args = [ast.literal_eval(a) for a in node.args]
        return self.visit(ast.Tuple(elts=[ast.Constant(value=i) for i in range(*args)]))

    def __call_len(self, node: ast.Call):
        if len(node.args) != 1:
            raise Exception(f"len() takes exactly 1 argument ({len(node.args)} given)")
        return const_to_qtype(len(self.__unroll_arg(node.args[0])))

    def __call_sum(self, node: ast.Call):
        if len(node.args) != 1:
            raise Exception(f"sum() takes exactly 1 argument ({len(node.args)} given)")

        def rec(lst):
            if len(lst) == 1:
                return lst[0]
            return lst[0][0].add(lst[0], rec(lst[1:]))

        return rec(self.__unroll_arg(node.args[0]))

    def __call_anyall(self, node: ast.Call):
        if len(node.args) != 1:
            raise Exception(
                f"{node.func.id}() takes exactly 1 "  # type: ignore
                + f"argument ({len(node.args)} given)"
            )
        op = Or if node.func.id == "any" else And  # type: ignore
        return (bool, op(*[a[1] for a in self.__unroll_arg(node.args[0])]))

    def __call_ord(self, node: ast.Call):
        if len(node.args) != 1:
            raise Exception(f"ord() takes exactly 1 argument ({len(node.args)} given)")
        return self.visit(node.args[0])

    def __call_chr(self, node: ast.Call):
        if len(node.args) != 1:
            raise Exception(f"chr() takes exactly 1 argument ({len(node.args)} given)")
        return self.visit(node.args[0])

    def __call_minmax(self, node: ast.Call):
        if len(node.args) == 1:
            args = self.__unroll_arg(node.args[0])
        else:
            args = [self.visit(a) for a in node.args]
        cmp = "gt" if node.func.id == "max" else "lte"  # type: ignore

        def rec(lst):
            if len(lst) == 1:
                return lst[0]
            conds = [getattr(lst[0][0], cmp)(lst[0], x)[1] for x in lst[1:]]
            cond = And(*conds)
            t, v = lst[0]
            _, v2 = rec(lst[1:])
            if isinstance(v, list) or isinstance(v2, list):
                # multi-bit elements: ITE elementwise
                va = v if isinstance(v, list) else [v] * len(v2)
                vb = v2 if isinstance(v2, list) else [v2] * len(va)
                return (t, [ITE(cond, a, b) for a, b in zip(va, vb)])
            return (t, ITE(cond, v, v2))

        return rec(args)

    def __visit_Call_typecast(self, expr):
        if len(expr.args) != 1:
            raise Exception(
                f"{expr.func.id}() takes exactly 1 argument ({len(expr.args)} given)"
            )

        if not isinstance(expr.args[0], ast.Constant):
            raise Exception(f"{expr.func.id}() accepts only constant values")

        return self.env.gettype(expr.func.id).const(expr.args[0].value)

    def __visit_Call_int(self, expr):
        if len(expr.args) != 1:
            raise Exception(f"int() takes exactly 1 argument ({len(expr.args)} given)")

        ta, te = self.visit(expr.args[0])
        if ta.__name__[:4] == "Qint":
            return (ta, te)
        elif ta.__name__[:6] == "Qfixed":
            ip = ta.integer_part((ta, te))  # type: ignore
            return (Qint.type_for_size(len(ip)), ip)
        else:
            raise Exception(f"int() accepts only Qfixed and Qint: {ta} given")

    def __visit_Call_float(self, expr):
        if len(expr.args) != 1:
            raise Exception(
                f"float() takes exactly 1 argument ({len(expr.args)} given)"
            )

        ta, te = self.visit(expr.args[0])
        if ta.__name__[:6] == "Qfixed":
            return (ta, te)
        elif ta.__name__[:4] == "Qint":
            tf = Qfixed.type_for_size(len(te))
            return cast(TExp, tf.fill((tf, te)))
        else:
            raise Exception(f"float() accepts only Qfixed and Qint: {ta} given")

    def __visit_Call_known_function(self, expr):
        def_f = self.env.getdef(expr.func.id)
        args = [self.visit(e) for e in expr.args]

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

    # Call
    def visit_Call(self, expr: ast.Call):
        # Quantum hybrid
        if (
            isinstance(expr.func, ast.Attribute)
            and isinstance(expr.func.value, ast.Name)
            and expr.func.value.id == "Q"
        ):
            gate = expr.func.attr
            args = [self.visit(e) for e in expr.args]
            args_v = [b for (a, b) in args]

            q_gate = QuantumBooleanGate.build(gate)

            if len(args_v) == 1 and isinstance(args_v[0], list):
                return args[0][0], [q_gate(a) for a in args_v[0]]
            else:
                return args[0][0], q_gate(*args_v)

        elif not hasattr(expr.func, "id"):
            raise exceptions.ExpressionNotHandledException(expr)

        # Builtin functions
        elif expr.func.id in self.__call_dispatch:
            return self.__call_dispatch[expr.func.id](expr)

        # Typecast
        elif self.env.know_type(expr.func.id):
            return self.__visit_Call_typecast(expr)

        # Print
        elif expr.func.id == "print":
            return [], self.env

        # int()
        elif expr.func.id == "int":
            return self.__visit_Call_int(expr)

        # float()
        elif expr.func.id == "float":
            return self.__visit_Call_float(expr)

        # Known function
        elif self.env.know_function(expr.func.id):
            return self.__visit_Call_known_function(expr)

        raise exceptions.UnknownSymbolException(expr.func.id, self.env)

    # Lambda
    # Dict
    # Set

    def generic_visit(self, expr):
        raise exceptions.ExpressionNotHandledException(expr)


def translate_expression(expr, env: Env) -> TExp:
    """Translate an expression"""
    return ExpressionTranslator(env).visit(expr)  # type: ignore
