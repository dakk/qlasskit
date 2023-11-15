from copy import deepcopy
from sympy import Function
from sympy.logic.boolalg import Boolean


class QuantumBooleanGate(Function, Boolean):
    def build(name: str):
        return type(name, (QuantumBooleanGate,), { }) 


class Q:
    """An identity wrapper for python"""

    def H(*args):
        return args

    def Z(*args):
        return args

    def Y(*args):
        return args

    def X(*args):
        return args

    def T(*args):
        return args

    def S(*args):
        return args

    def CX(*args):
        return args

    def MCX(*args):
        return args
