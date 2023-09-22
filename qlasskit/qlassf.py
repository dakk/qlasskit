
""" Class representing a quantum classical circuit """
class QlassF:
    def __init__(self):
        pass 

    """ The gate """
    @property
    def gate(self, framework='qiskit'):
        return None 

    """ List of qubits of the gate """
    @property
    def qubits(self, index=0):
        return []

    """ Return a new QlassF with defined params """
    def bind(self, **kwargs):
        pass 

    """ Return the classical python function """
    def f(self):
        pass 

    
""" Decorator creating a QlassF object """
def qlassf(f):
    return QlassF()


