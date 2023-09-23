import ast 

from sympy import Symbol
from sympy.logic import And, Not, Or, false, true, simplify_logic

from . import exceptions

flatten = lambda m: [item for row in m for item in row]

def parse_arguments(args):
    """ Parse an argument list """
    def map_arg(arg):
        to_name = lambda a: a.attr if isinstance(a, ast.Attribute) else a.id
        
        if isinstance(arg.annotation, ast.Subscript):
            al = []
            for i in arg.annotation.slice.elts:
                al.append((f'{arg.arg}.{len(al)}', to_name(i)))
            return al
        elif to_name(arg.annotation)[0:3] == 'Int':
            n = int(to_name(arg.annotation)[3::])
            l = [(f'{arg.arg}.{i}', 'bool') for i in range(n)]
            l.append((f'{arg.arg}', n))
            return l
        else:
            return [(arg.arg, to_name(arg.annotation))]
        
    return flatten(list(map(map_arg, args)))


def parse_expression(expr, env):
    """ Parse an expression """
    match expr:
        case ast.Name():
            if expr.id not in env:
                raise UnboundException(expr.id)
            return Symbol(expr.id)
        
        case ast.Subscript():
            sn = f'{expr.value.id}.{expr.slice.value}'
            if sn not in env:
                raise UnboundException(sn)
            return Symbol(sn)

        case ast.BoolOp():
            def unfold(l, op):
                c_exp = lambda l: op(l[0], c_exp(l[1::])) if len(l) > 1 else l[0]
                return c_exp(v_exps)
                
            v_exps = [parse_expression(e_in, env) for e_in in expr.values]
            
            match expr.op:
                case ast.And():
                    return unfold(v_exps, And)
                case ast.Or():
                    return unfold(v_exps, Or)
                case _:
                    raise ExpressionNotHandledException(expr)

        case ast.UnaryOp():
            match expr.op:
                case ast.Not():
                    return Not(parse_expression(expr.operand, env))
                case _:
                    raise ExpressionNotHandledException(expr)

        # (condition) and (true_value) or (not condition) and (false_value)
        case ast.IfExp():
            raise exceptions.ExpressionNotHandledException(expr)
            
        case ast.Constant():
            match expr.value:
                case True:
                    return true
                case False:
                    return false
                case _:
                    raise exceptions.ExpressionNotHandledException(expr)
                
        case ast.Tuple():
            raise exceptions.ExpressionNotHandledException(expr)
        
        case ast.Compare():
            raise exceptions.ExpressionNotHandledException(expr)
 
        case _:
            raise ExpressionNotHandledException(expr)


def parse_statement(stmt, env):
    """ Parse a statement """
    match stmt:
        case ast.If():
            raise exceptions.StatementNotHandledException(stmt) 
        
        case ast.Assign():
            raise exceptions.StatementNotHandledException(stmt) 

        case ast.Return():
            vexp = parse_expression(stmt.value, env)
            return [('_ret', vexp)], env
        
        case _:
            raise exceptions.StatementNotHandledException(stmt)