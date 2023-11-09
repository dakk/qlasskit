from matplotlib import pyplot as plt
from qiskit import QuantumCircuit

from qlasskit import Qint2, qlassf

INTSIZ = 2


@qlassf
def f1(b: bool, n: Qint2) -> Qint2:
    return n + (1 if b else 2)


@qlassf
def f_comp(b: bool, n: Qint2) -> Qint2:
    for i in range(3):
        n += 1 if b else 2
    return n


print(f_comp.expressions)
f_comp.compile("tweedledum")
qc = QuantumCircuit(f_comp.num_qubits)
qc.barrier(label="f_comp")
qc.append(f_comp.gate(), f_comp.qubits)
print(qc.decompose().draw("text"))
print(qc.decompose().count_ops())

print(
    qc.decompose().draw(
        "mpl",
        style={"textcolor": "#ffab40", "backgroundcolor": "black", "linecolor": "#444"},
    )
)

f1.compile("tweedledum")
qc = QuantumCircuit(f_comp.num_qubits * 2)

for i in range(3):
    qc.barrier(label=f"it_{i}")
    qc.append(f1.gate(), [0] + list(range(1 + i * INTSIZ, 1 + i * INTSIZ + INTSIZ * 2)))

print(qc.decompose().draw("text"))
print(qc.decompose().count_ops())
print(
    qc.decompose().draw(
        "mpl",
        style={"textcolor": "#ffab40", "backgroundcolor": "black", "linecolor": "#444"},
    )
)
plt.show()
