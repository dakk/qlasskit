import ast 

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
            raise exceptions.ExpressionNotHandledException(e)

        case ast.UnaryOp():
            raise exceptions.ExpressionNotHandledException(e)

        # (condition) and (true_value) or (not condition) and (false_value)
        case ast.IfExp():
            raise exceptions.ExpressionNotHandledException(e)
            
        case ast.Constant():
            match expr.value:
                case True:
                    return true
                case False:
                    return false
                case _:
                    raise exceptions.ExpressionNotHandledException(e)
                
        case ast.Tuple():
            raise exceptions.ExpressionNotHandledException(e)
        
        case ast.Compare():
            raise exceptions.ExpressionNotHandledException(e)
 
        case _:
            raise ExpressionNotHandledException(e)


def parse_statement(stmt, env):
    """ Parse a statement """
    match stmt:
        case ast.If():
            raise exceptions.StatementNotHandledException(stmt) 
        
        case ast.Assign():
            raise exceptions.StatementNotHandledException(stmt) 

        case ast.Return():
            raise exceptions.StatementNotHandledException(stmt) 
        
        case _:
            raise exceptions.StatementNotHandledException(stmt)