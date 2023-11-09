from qiskit import QuantumCircuit

from qlasskit import Qint4, qlassf


@qlassf
def f_comp(n: Qint4) -> bool:
    return n > 3 or n == 7


qc = QuantumCircuit(f_comp.num_qubits, f_comp.num_qubits)

qc.initialize(f_comp.inputs, f_comp.encode_input(Qint4(12)))

qc.append(f_comp.gate(), f_comp.qubits)

qc.measure(f_comp.outputs)

## Get result
qval = f_comp.decode_output(measurement)
print("Bool:", qval)
