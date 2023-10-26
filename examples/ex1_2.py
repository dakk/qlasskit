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
gate = f_comp.gate()
qc = QuantumCircuit(gate.num_qubits)
qc.barrier(label="f_comp")
qc.append(gate, list(range(gate.num_qubits)))
print(qc.decompose().draw("text"))
print(qc.decompose().count_ops())


gate1 = f1.gate()
qc = QuantumCircuit(gate.num_qubits * 3)

for i in range(3):
    qc.barrier(label="=")
    qc.append(gate1, [0] + list(range(1 + i * INTSIZ, 1 + i * INTSIZ + INTSIZ * 2)))

print(qc.decompose().draw("text"))
print(qc.decompose().count_ops())
