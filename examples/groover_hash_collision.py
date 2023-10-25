from qiskit import Aer, QuantumCircuit, transpile

from qlasskit import Qint4, qlassf

# from qlasskit.algorithms import Groover


# @qlassf
# def hash(k: Qint4) -> Tuple[bool, bool]:
#     h = (False, False)
#     for i in range(4):
#         h = (h[0] or k[i], not h[1] and k[i])
#     return h


@qlassf
def hash(k: Qint4) -> bool:
    h = False
    for i in range(4):
        h = h or k[i]
    return h


# @qlassf(defs=[hash])
# def find_coll(k: Qint4):
#     return hash(k) == 0b0101


print(hash)


# algo = Groover(hash, True, 12)
# qc = algo.export('qiskit')
# ### EXEC
# algo.interpret_output()

qc = hash.circuit().export("circuit")
print(qc.draw("text"))

# gate = hash.gate()
# qc = QuantumCircuit(gate.num_qubits)
# qc.barrier(label="hash")
# qc.append(gate, list(range(gate.num_qubits)))
# print(qc.decompose().draw("text"))
# print(qc.decompose().count_ops())


# simulator = Aer.get_backend("aer_simulator")
# circ = transpile(qc, simulator)
# result = simulator.run(circ).result()
# counts = result.get_counts(circ)
# print(counts)
