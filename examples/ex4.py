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
gate = f_comp.gate()
qc = QuantumCircuit(gate.num_qubits)
qc.append(gate, list(range(gate.num_qubits)))
print(qc.decompose().count_ops())
print(qc.decompose().draw("text"))


print(f1.expressions, f2.expressions)
gate1 = f1.gate()
gate2 = f2.gate()
qc = QuantumCircuit(-2 + gate1.num_qubits + gate2.num_qubits)
qc.append(gate1, list(range(gate1.num_qubits)))
qc.barrier()
qc.append(
    gate2, list(range(gate1.num_qubits - 2, gate1.num_qubits + gate2.num_qubits - 2))
)

print(qc.decompose().count_ops())
print(qc.decompose().draw("text"))
