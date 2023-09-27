from qiskit import Aer, QuantumCircuit, transpile

from qlasskit import qlassf


@qlassf
def f(a: bool, b: bool) -> bool:
    return a and not b


print(f"\n{f}\n")

qc = QuantumCircuit(f.num_qubits, 1)
qc.x(0)  # a = true
qc.barrier()
qc.append(f.gate(), f.qubits(0))
qc.barrier()
qc.measure(f.res_qubits[0], 0)

print(qc.draw())
print(qc.decompose().draw())

simulator = Aer.get_backend("aer_simulator")
circ = transpile(qc, simulator)
result = simulator.run(circ).result()
counts = result.get_counts(circ)
print(counts)


# qc.save_unitary()
# simulator = Aer.get_backend('unitary_simulator')
# result = execute(qc, simulator).result().get_unitary(qc)
# print(result)
