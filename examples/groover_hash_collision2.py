from typing import Tuple

from matplotlib import pyplot as plt
from qiskit import Aer, ClassicalRegister, QuantumCircuit, transpile
from qiskit.visualization import plot_histogram

from qlasskit import Qint2, Qint4, Qint8, Qint16, Qlist, qlassf
from qlasskit.algorithms import Groover


def qiskit_simulate(qc, alog):
    c = ClassicalRegister(len(algo.out_qubits()))
    qc.add_bits(c)
    qc.measure(algo.out_qubits(), c)
    print(qc.draw("text"))

    # simulator = Aer.get_backend("aer_simulator")
    # circ = transpile(qc, simulator, optimization_level=3)

    from pyqrack import qrack_simulator
    from qiskit.providers.qrack import Qrack

    simulator = Qrack.get_backend("qasm_simulator")
    circ = transpile(qc, simulator)

    result = simulator.run(circ).result()
    return result.get_counts(circ)


# @qlassf
# def md5_simp(message: Tuple[Qint8, Qint8]) -> Qint8:
#     A = 0x12
#     # A, B, C, D = 0x12, 0x34, 0x56, 0x78

#     for i in range(2):  # MESSAGE_LEN
#         char = message[i]

#         A = (A + char) & 0xFF
#         # B = (B ^ char) & 0xFF
#         # C = (C + (char << 1)) & 0xFF
#         # D = (D - char) & 0xFF

#     # return (A<<8) + B
#     return A


# @qlassf
# def md5_simp(message: Qlist[Qint4, 2]) -> Qint4:
#     A = 0x12
#     B = 0x34
#     C = 0x56
#     D = 0x78

#     for char in message:
#         A = (A + char) & 0xF
#         B = (B ^ char) & 0xF
#         C = (C + (char << 1)) & 0xF
#         D = (D - char) & 0xF

#     return A + (B << 1) + (C << 2) + (D << 3)


@qlassf
def md5_simp(m: Tuple[Qint2, Qint2]) -> Qint4:
    A = 0x1
    B = 0x3
    A = (A + m[0]) & 0xF
    B = (B ^ m[1]) & 0xF
    return (A << 2) + B


# print(md5_simp.expressions)
# print(md5_simp.circuit().export('circuit', 'qiskit').draw('text'))
algo = Groover(md5_simp, (Qint4(0)))

# print(hex(md5_simp.original_f((2,3))))

qc = algo.circuit().export("circuit", "qiskit")
counts = qiskit_simulate(qc, algo)
counts_readable = algo.interpet_counts(counts)
plot_histogram(counts_readable)
plt.show()


# print(md5_simp.circuit().export("circuit", "qiskit").draw("text"))
# plt.show()
