import ast
from typing import Dict, List, Tuple, Union

from sympy import Symbol
from sympy.logic import ITE, And, Implies, Not, Or, false, simplify_logic, true

from . import exceptions, utils

BoolExp = Union[Symbol, And, Or, Not, ITE, type(false), type(true)]
Env = Dict[str, str]


def translate_arguments(args) -> List[Tuple[str, str]]:
    """Parse an argument list"""

    def map_arg(arg):
        to_name = lambda a: a.attr if isinstance(a, ast.Attribute) else a.id

        if isinstance(arg.annotation, ast.Subscript):
            al = []
            for i in arg.annotation.slice.elts:
                al.append((f"{arg.arg}.{len(al)}", to_name(i)))
            return al
        elif to_name(arg.annotation)[0:3] == "Int":
            n = int(to_name(arg.annotation)[3::])
            l = [(f"{arg.arg}.{i}", "bool") for i in range(n)]
            l.append((f"{arg.arg}", n))
            return l
        else:
            return [(arg.arg, to_name(arg.annotation))]

    return utils.flatten(list(map(map_arg, args)))


def translate_expression(expr: ast.Expr, env: Env) -> BoolExp:
    """Translate an expression"""
    if expr == ast.Name():
        if expr.id not in env:
            raise UnboundException(expr.id)
        return Symbol(expr.id)

    elif expr == ast.Subscript():
        sn = f"{expr.value.id}.{expr.slice.value}"
        if sn not in env:
            raise UnboundException(sn)
        return Symbol(sn)

    elif expr == ast.BoolOp():

        def unfold(l, op):
            c_exp = lambda l: op(l[0], c_exp(l[1::])) if len(l) > 1 else l[0]
            return c_exp(v_exps)

        v_exps = [translate_expression(e_in, env) for e_in in expr.values]

        return unfold(v_exps, And if expr.op == ast.And() else Or)

    elif expr == ast.UnaryOp():
        if expr.op == Not():
            return Not(translate_expression(expr.operand, env))
        else:
            raise ExpressionNotHandledException(expr)

    elif expr == ast.IfExp():
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

    elif expr == ast.Constant():
        if expr.value == True:
            return true
        elif expr.value == False:
            return false
        else:
            raise exceptions.ExpressionNotHandledException(expr)

    elif expr == ast.Tuple():
        raise exceptions.ExpressionNotHandledException(expr)

    elif expr == ast.Compare():
        # Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
        raise exceptions.ExpressionNotHandledException(expr)

    # Lambda
    # Dict
    # Set
    # Call
    # List
    # op Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv

    else:
        raise ExpressionNotHandledException(expr)


def translate_statement(stmt, env: Env) -> Tuple[List[Tuple[str, BoolExp]], Env]:
    """Parse a statement"""
    # match stmt:
    if stmt == ast.If():
        raise exceptions.StatementNotHandledException(stmt)

    elif stmt == ast.Assign():
        raise exceptions.StatementNotHandledException(stmt)

    elif stmt == ast.Return():
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
