from typing import Tuple

from matplotlib import pyplot as plt
from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

from qlasskit import Qint2, qlassf
from qlasskit.algorithms import Grover


def qiskit_simulate(qc):
    qc.measure_all()

    simulator = Aer.get_backend("aer_simulator")
    circ = transpile(qc, simulator)
    result = simulator.run(circ).result()

    return result.get_counts(circ)


@qlassf
def subset_sum(ii: Tuple[Qint2, Qint2]) -> Qint2:
    l = [0, 1, 2, 0]
    ai, bi = ii
    a = l[ai]
    b = l[bi]
    return a + b


algo = Grover(subset_sum, Qint2(3))

qc = algo.circuit().export("circuit", "qiskit")
print(qc.draw("text"))
counts = qiskit_simulate(qc)
counts_readable = algo.decode_counts(counts)
plot_histogram(counts_readable)
plt.show()
