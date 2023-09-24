""" Algorithm and functions able to synthetize a boolean function to a quantum circuit """
from sympy import Symbol
from sympy.logic import ITE, Implies, And, Not, Or, false, true, simplify_logic

def to_qiskit(gl, resbit, qmap):
    from qiskit import QuantumCircuit
    from qiskit import Aer, transpile, execute
    
    qc = QuantumCircuit(len(qmap), 0)
    
    # qc.x(1)
    # qc.barrier()
    for g in gl:
        match g[0]:
            case 'x':
                qc.x(g[1])
            case 'cx':
                qc.cx(g[1], g[2])
            case 'ccx':
                qc.ccx(g[1], g[2], g[3])
    # qc.barrier()
    # qc.measure(resbit, 0)
    print(qc.draw())
    
    # simulator = Aer.get_backend('aer_simulator')
    # circ = transpile(qc, simulator)
    # result = simulator.run(circ).result()
    # counts = result.get_counts(circ)
    # print(counts)
    
    print (qc.to_gate())
    
    
    # qc.save_unitary()
    simulator = Aer.get_backend('unitary_simulator')
    result = execute(qc, simulator).result().get_unitary(qc)
    print(result)
    

class Synthetizer:
    def __init__(self):
        self.qmap = {}
        
    def synth(self, expr):
        raise Exception('abstract')

class Synthetizer_0(Synthetizer):        
    def synth(self, expr):
        match expr:
            case Symbol():
                # print('sym', expr.name)
                if expr.name not in self.qmap:
                    self.qmap[expr.name] = len(self.qmap)
                return self.qmap[expr.name], []
            
            case Not():
                # print('NOT', expr.args)
                i, g = self.synth(expr.args[0])
                return i, g + [('x', i)]
            
            case And():
                il = []
                gl = []
                
                for x in expr.args:
                    ii, gg = self.synth(x)
                    il.append(ii)
                    gl.extend(gg)
                    
                iold = il[0]
                for x in range (1,len(il)):
                    inew = len(self.qmap)
                    self.qmap[f'anc_{len(self.qmap)}'] = inew
                    gl.append(('ccx', iold, il[x], inew))
                    iold = inew

                return inew, gl
                
            case Or():
                if len(expr.args) > 2:
                    raise Exception ("too many clause")
                
                i1, g1 = self.synth(expr.args[0])
                i2, g2 = self.synth(expr.args[1])
                i3 = len(self.qmap)
                self.qmap[f'anc_{len(self.qmap)}'] = i3

                return i3, g1 + g2 + [('x', i2), ('ccx', i1, i2, i3), ('x', i2), ('cx', i2, i3)]
            
            case _:
                print('notrec', expr)


def to_quantum(bexp):
    s = Synthetizer_0()
    c = s.synth(bexp)
    print('res',c, s.qmap)
    to_qiskit(c[1], c[0], s.qmap)