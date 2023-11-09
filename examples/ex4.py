from qiskit import QuantumCircuit

from qlasskit import Qint2, qlassf


@qlassf
def f1(n: Qint2, q: Qint2) -> Qint2:
    return n + q


@qlassf
def f2(n: Qint2, z: Qint2) -> Qint2:
    return n - (z if n > z else n - 1)


@qlassf
def f_comp(n: Qint2, q: Qint2, z: Qint2) -> Qint2:
    c = n + q
    return c - (z if c > z else (c - 1))


# from sympy import simplify_logic

print(f_comp.expressions)
# print(simplify_logic(f_comp.expressions[1][1]))
qc = QuantumCircuit(f_comp.num_qubits)
qc.append(f_comp.gate(), f_comp.qubits)
print(qc.decompose().count_ops())
print(qc.decompose().draw("text"))


print(f1.expressions, f2.expressions)
qc = QuantumCircuit(-2 + f1.num_qubits + f1.num_qubits)
qc.append(f1.gate(), f1.qubits)
qc.barrier()
qc.append(f2.gate(), list(range(f1.num_qubits - 2, f1.num_qubits + f1.num_qubits - 2)))

print(qc.decompose().count_ops())
print(qc.decompose().draw("text"))
