from qiskit import QuantumCircuit

from qlasskit import Qint4, qlassf


@qlassf
def f1(n: Qint4) -> bool:
    return n == 7


@qlassf
def f2(n: Qint4, b: bool) -> bool:
    return n > 3


@qlassf
def f3(a: bool, b: bool) -> bool:
    return a or b


@qlassf
def f_comp(n: Qint4) -> bool:
    return n > 3 or n == 7


print(f_comp.expressions)
gate = f_comp.gate()
qc = QuantumCircuit(gate.num_qubits)
qc.barrier(label="f_comp")
qc.append(gate, list(range(gate.num_qubits)))
print(qc.decompose().draw("text"))
print (qc.decompose().count_ops())


gate1 = f1.gate()
gate2 = f2.gate()
gate3 = f3.gate()
qc = QuantumCircuit(max(gate1.num_qubits, gate2.num_qubits) + gate3.num_qubits)
qc.barrier(label="=")
qc.append(gate1, [0, 1, 2, 3, 4, 5])
qc.barrier(label=">")
qc.append(gate2, [0, 1, 2, 3, 6, 7, 8, 9])
qc.barrier(label="|")
qc.append(gate3, [5, 9, 10, 11, 12])
print(qc.decompose().draw("text"))
print (qc.decompose().count_ops())
