import ast
import inspect 

from sympy import Symbol
from sympy.logic import And, Not, Or, false, true, simplify_logic

from .ast_parser import parse_arguments, parse_expression, parse_statement
from . import exceptions

class QlassF:
    """Class representing a quantum classical circuit"""

    def __init__(self, name, original_f):
        self.name = name
        self.original_f
    
    def __repr__(self):
        return f'QlassF("{self.name}")'

    @property
    def gate(self, framework="qiskit"):
        """Returns the gate for a specific framework"""
        return None

    @property
    def qubits(self, index=0):
        """List of qubits of the gate"""
        return []

    def bind(self, **kwargs):
        """Returns a new QlassF with defined params"""
        pass

    def f(self):
        """Returns the classical python function"""
        return original_f


def qlassf(f):
    """Decorator / function creating a QlassF object"""
    fun_ast = ast.parse(f) if type(f) == str else ast.parse(inspect.getsource(f))        
    fun = fun_ast.body[0]    
    fun_name = fun.name
    
    print(ast.dump(fun))
    
    env = {}
    
    args = parse_arguments(fun.args.args)
    # print(args)
    # TODO: types are string; maybe a parse_type?
    for (a_name, a_type) in args:
        env[a_name] = a_type
    
    if not fun.returns:
        raise exceptions.NoReturnTypeException()
    fun_ret = fun.returns.id
    # TODO: handle complex returns
    # print(fun_ret)
    
    for stmt in fun.body:
        s_exps, env = parse_statement(stmt, env)

    return QlassF(fun_name, f)
