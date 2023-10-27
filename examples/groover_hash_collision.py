from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from matplotlib import pyplot as plt

from qlasskit import Qint8, Qint4, qlassf
from qlasskit.algorithms import Groover


# @qlassf
# def hash(k: Qint8) -> Qint8:
#     return (k<<1)+2

# algo = Groover(hash, Qint8(12))

# @qlassf
# def hash(k: Qint4) -> bool:
#     h = True
#     for i in range(4):
#         h = h and k[i]
#     return h

# algo = Groover(hash, True)


# @qlassf
# def hash(k: Qint4) -> Qint4:
#     def inner(q: Qint4) -> bool:
#         return q > 8
    
#     return (k<<1) + 2 if inner(k) else 4

@qlassf
def hash(k: Qint4) -> Qint4:
    return (k<<1) + 2

algo = Groover(hash, Qint4(12))

# Export the circuit
qc = algo.circuit().export("circuit", 'qiskit')
qc.measure(algo.out_qubits(), algo.out_qubits())
print(qc.draw("text"))

# Simulate the circuit
simulator = Aer.get_backend("aer_simulator")
circ = transpile(qc, simulator)
result = simulator.run(circ).result()

# Get and show interpreted result counts
counts = result.get_counts(circ)
counts_readable = algo.interpet_counts(counts)
plot_histogram(counts_readable)
plt.show()





# Export the circuit
qc = algo.circuit().export("circuit", 'qiskit')
qc.measure(algo.out_qubits(), algo.out_qubits())
print(qc.draw("text"))

# Simulate the circuit
simulator = Aer.get_backend("aer_simulator")
circ = transpile(qc, simulator)
result = simulator.run(circ).result()

# Get and show interpreted result counts
counts = result.get_counts(circ)
counts_readable = algo.interpet_counts(counts)
plot_histogram(counts_readable)
plt.show()



print (hash.circuit().export("circuit", 'qiskit').draw('text'))
