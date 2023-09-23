
class QlassF:
    """ Class representing a quantum classical circuit """
    def __init__(self):
        pass 

    @property
    def gate(self, framework='qiskit'):
        """ The gate """
        return None 

    @property
    def qubits(self, index=0):
        """ List of qubits of the gate """
        return []

    def bind(self, **kwargs):
        """ Return a new QlassF with defined params """
        pass 

    def f(self):
        """ Return the classical python function """
        pass 

    
def qlassf(f):
    """ Decorator creating a QlassF object """
    return QlassF()


