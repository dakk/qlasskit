# Copyright 2023 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

from qlasskit import QlassF

COMPILATION_ENABLED = True


def test_not(a: bool) -> bool:
    return not a


# def get_qlassf_input_bits(qf: QlassF) -> int:
#     pass


# def get_input_combinations(n_bits: int) -> List[List[bool]]:
#     pass


# def compute_originalf_results(qf: QlassF) -> List[List[bool]]:
#     pass

aer_simulator = Aer.get_backend("aer_simulator")


def qiskit_measure_and_count(circ, shots=1):
    circ.measure_all()
    circ = transpile(circ, aer_simulator)
    result = aer_simulator.run(circ, shots=shots).result()
    counts = result.get_counts(circ)
    return counts


def compare_circuit_truth_table(cls, qf):
    if not COMPILATION_ENABLED:
        return
    truth_table = qf.truth_table()
    gate = qf.gate()
    circ = qf.circuit()
    circ_qi = circ.export("circuit", "qiskit")
    print(circ_qi.draw("text"))

    for truth_line in truth_table:
        qc = QuantumCircuit(gate.num_qubits)

        # Prepare inputs
        for i in range(qf.input_size):
            qc.initialize(1 if truth_line[i] else 0, i)

        # (truth_line)

        qc.append(gate, list(range(qf.num_qubits)))
        # print(qc.decompose().draw("text"))

        counts = qiskit_measure_and_count(qc)
        # print(counts, circ.qubit_map)

        truth_str = "".join(
            map(lambda x: "1" if x else "0", truth_line[-qf.ret_size :])
        )

        # print(truth_str)

        res = list(counts.keys())[0][::-1]
        res_str = ""
        for qname in qf.truth_table_header()[-qf.ret_size :]:
            res_str += res[circ.qubit_map[qname]]

        # res = res[0 : len(truth_str)][::-1]
        # print(res_str)

        cls.assertEqual(len(counts), 1)
        cls.assertEqual(truth_str, res_str)

    # cls.assertLessEqual(gate.num_qubits, len(qf.truth_table_header()))
