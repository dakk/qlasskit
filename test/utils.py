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


def test_not(a: bool) -> bool:
    return not a


# def get_qlassf_input_bits(qf: QlassF) -> int:
#     pass


# def get_input_combinations(n_bits: int) -> List[List[bool]]:
#     pass


# def compute_originalf_results(qf: QlassF) -> List[List[bool]]:
#     pass


def qiskit_measure_and_count(circ):
    circ.measure_all()
    simulator = Aer.get_backend("aer_simulator")
    circ = transpile(circ, simulator)
    result = simulator.run(circ).result()
    counts = result.get_counts(circ)
    return counts


def compare_circuit_truth_table(cls, qf):
    truth_table = qf.truth_table()
    gate = qf.gate()

    for truth_line in truth_table:
        qc = QuantumCircuit(gate.num_qubits)

        # Prepare inputs
        for i in range(qf.input_size):
            qc.initialize(1 if truth_line[i] else 0, i)

        qc.append(gate, list(range(qf.num_qubits)))
        counts = qiskit_measure_and_count(qc)

        print(qc.decompose().draw("text"))
        print(counts)

        truth_str = "".join(
            map(lambda x: "1" if x else "0", truth_line[-qf.ret_size :])
        )

        cls.assertEqual(len(counts), 1)
        cls.assertEqual(truth_str, list(counts.keys())[0][0 : len(truth_str)])
