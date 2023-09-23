import ast
import inspect 

from .ast_parser import parse_arguments, parse_expression, parse_statement, flatten
from .exceptions import NoReturnTypeException

class QlassF:
    """Class representing a quantum classical circuit"""
    def __init__(self, name, original_f, args, exps):
        self.name = name
        self.original_f = original_f # TODO: this should be always a callable (not a str)
        self.args = args
        self.expressions = exps
    
    def __repr__(self):
        arg_str = ", ".join(map(lambda arg: f'{arg[0]}:{arg[1]}',self.args))
        exp_str = "\n\t".join(map(lambda exp: f'{exp[0]} = {exp[1]}', self.expressions))
        return f'QlassF<{self.name}>({arg_str}):\n\t{exp_str}'
    
    def from_function(f):
        """ Create a QlassF from a function """
        fun_ast = ast.parse(f) if type(f) == str else ast.parse(inspect.getsource(f))        
        fun = fun_ast.body[0]    
        fun_name = fun.name
        
        # env contains names visible from the current scope
        env = {}
        
        args = parse_arguments(fun.args.args)
        # TODO: types are string; maybe a parse_type?
        for (a_name, a_type) in args:
            env[a_name] = a_type
        
        if not fun.returns:
            raise NoReturnTypeException()
        fun_ret = fun.returns.id
        # TODO: handle complex-type returns
        
        exps = []
        for stmt in fun.body:
            s_exps, env = parse_statement(stmt, env)
            exps.append(s_exps)
            
        exps = flatten (exps)
        
        qf = QlassF(fun_name, f, args, exps)    
        print(qf)
        return qf

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
    return QlassF.from_function(f)