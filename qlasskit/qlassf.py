import ast
import inspect 
from typing import List

from sympy.logic import simplify_logic

from .ast_parser import parse_arguments, parse_expression, parse_statement, flatten
from .exceptions import NoReturnTypeException
from . import synth

class QlassF:
    """Class representing a quantum classical circuit"""
    def __init__(self, name, original_f, args, ret_type, exps):
        self.name = name
        self.original_f = original_f # TODO: this should be always a callable (not a str)
        self.args = args
        self.ret_type = ret_type
        self.expressions = exps
        
        self._synthetized_gate = None
        
    def synth(self):
        # TODO: synthetize all expression and create a one gate only
        self._synthetized_gate = synth.to_quantum(self.expressions[0][-1])
    
    def __repr__(self):
        arg_str = ", ".join(map(lambda arg: f'{arg[0]}:{arg[1]}',self.args))
        exp_str = "\n\t".join(map(lambda exp: f'{exp[0]} = {exp[1]}', self.expressions))
        return f'QlassF<{self.name}>({arg_str}) -> {self.ret_type}:\n\t{exp_str}'
    
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
        exps = list(map (lambda e: simplify_logic(e, form='cnf'), exps))
        
        qf = QlassF(fun_name, f, args, fun_ret, exps)    
        
        # print(qf)
        qf.synth()
        return qf

    @property
    def gate(self, framework="qiskit"):
        """Returns the gate for a specific framework"""
        if self._synthetized_gate is None:
            raise Exception ("Not yet synthetized")
        
        match framework:
            case 'qiskit':
                g = self._synthetized_gate.to_qiskit()
                g.name = self.name
                return g
            case _:
                raise Exception(f'Framework {framework} not supported')

    def qubits(self, index=0):
        """List of qubits of the gate"""
        if self._synthetized_gate is None:
            raise Exception ("Not yet synthetized")
        return self._synthetized_gate.qubit_map.values()
    
    @property
    def res_qubits(self) -> List[int]:
        """ Return the qubits holding the result """
        return [self._synthetized_gate.res_qubit]

    @property
    def num_qubits(self) -> int:
        """ Return the number of qubits"""
        return len(self.qubits())

    def bind(self, **kwargs):
        """Returns a new QlassF with defined params"""
        pass

    def f(self):
        """Returns the classical python function"""
        return original_f


def qlassf(f):
    """Decorator / function creating a QlassF object"""
    return QlassF.from_function(f)