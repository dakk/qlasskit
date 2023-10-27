from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

from qlasskit import Qint4, qlassf

from qlasskit.algorithms import Groover


@qlassf
def hash(k: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h


print (hash.circuit().export("circuit", 'qiskit').draw('text'))

algo = Groover(hash, True)

qc = algo.circuit().export("circuit", 'qiskit')
qc.measure([0,1,2,3],[0,1,2,3])
print(qc.draw("text"))

simulator = Aer.get_backend("aer_simulator")
circ = transpile(qc, simulator)
result = simulator.run(circ).result()
counts = result.get_counts(circ)

counts_readable = algo.interpet_counts(counts)

from matplotlib import pyplot as plt
fig = plot_histogram(counts_readable)
print(fig)
plt.show()
