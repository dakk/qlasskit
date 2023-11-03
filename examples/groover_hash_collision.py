from matplotlib import pyplot as plt
from qiskit import Aer, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

from qlasskit import Qint4, Qint8, qlassf
from qlasskit.algorithms import Groover


def qiskit_simulate(qc):
    qc.measure_all()
    qc.draw(
        "mpl",
        style={"textcolor": "#ffab40", "backgroundcolor": "black", "linecolor": "#444"},
    )
    print(qc.draw("text"))

    # from pyqrack import qrack_simulator
    # from qiskit.providers.qrack import Qrack
    # simulator = Qrack.get_backend("qasm_simulator")

    simulator = Aer.get_backend("aer_simulator")
    circ = transpile(qc, simulator)
    result = simulator.run(circ).result()

    return result.get_counts(circ)


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


@qlassf
def hash(k: Qint4) -> bool:
    h = True
    for i in range(4):
        h = h and k[i]
    return h

algo = Groover(hash, True)


# @qlassf
# def hash(k: Qint4) -> Qint4:
#     def inner(q: Qint4) -> bool:
#         return q > 8

#     return (k<<1) + 2 if inner(k) else 4


# from typing import Tuple

# @qlassf
# def hash(k: Qint8) -> Tuple[bool, bool]:
#     return k[0] and k[1] and not k[2] and not k[3], k[4] and not k[5] and k[6] and not k[7]
# algo = Groover(hash, (True,True))


# @qlassf
# def hash(k: Qint8) -> bool:
#     return k[0] and k[1] and not k[2] and not k[3] and k[4] and not k[5] and k[6] and not k[7]

# algo = Groover(hash, True)


# @qlassf
# def hash(k: Qint4) -> Qint4:
#     return (k << 1) + 2


# algo = Groover(hash, Qint4(12))

qc = algo.circuit().export("circuit", "qiskit")
counts = qiskit_simulate(qc)
counts_readable = algo.interpet_counts(counts)
plot_histogram(counts_readable)
plt.show()

print(hash.expressions)
print(
    hash.circuit()
    .export("circuit", "qiskit")
    .draw(
        "mpl",
        style={"textcolor": "#ffab40", "backgroundcolor": "black", "linecolor": "#444"},
    )
)
plt.show()
