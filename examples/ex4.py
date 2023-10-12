from qiskit import QuantumCircuit

from qlasskit import Qint4, qlassf


@qlassf
def f1(n: Qint4) -> Qint4:
    return n + 1


@qlassf
def f2(n: Qint4) -> Qint4:
    return n + 3


@qlassf
def f_comp(n: Qint4) -> Qint4:
    return n + 1 + 3


print(f_comp.expressions)
gate = f_comp.gate()
qc = QuantumCircuit(gate.num_qubits)
qc.append(gate, list(range(gate.num_qubits)))
print(qc.decompose().draw("text"))


gate1 = f1.gate()
gate2 = f2.gate()
qc = QuantumCircuit(max(gate1.num_qubits, gate2.num_qubits))
qc.append(gate1, list(range(gate1.num_qubits)))
qc.append(gate2, list(range(gate2.num_qubits)))
print(qc.decompose().draw("text"))
