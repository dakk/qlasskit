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
qc = QuantumCircuit(f_comp.num_qubits)
qc.barrier(label="f_comp")
qc.append(f_comp.gate(), f_comp.qubits)
print(qc.decompose().draw("text"))
print(qc.decompose().count_ops())

qc = QuantumCircuit(12)
qc.barrier(label="=")
qc.append(f1.gate(), f1.qubits)

qc.barrier(label=">")
qc.append(f2.gate(), f2.qubits)

qc.barrier(label="|")
qc.append(f3.gate(), g3.qubits)

print(qc.decompose().draw("text"))
print(qc.decompose().count_ops())
