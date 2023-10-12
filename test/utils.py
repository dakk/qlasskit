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

import inspect
from typing import Tuple, get_args

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from sympy.logic.boolalg import gateinputcount

from qlasskit import QlassF, Qtype, compiler

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


def compute_result_of_qcircuit(cls, qf, truth_line):
    """Simulate the quantum circuit for a given truth_line containing inputs"""
    circ = qf.circuit()
    gate = qf.gate()
    qc = QuantumCircuit(gate.num_qubits)

    # circ_qi = circ.export("circuit", "qiskit")
    # print(circ_qi.draw("text"))
    # print(qf.expressions)

    # Prepare inputs
    [qc.initialize(1 if truth_line[i] else 0, i) for i in range(qf.input_size)]

    qc.append(gate, list(range(qf.num_qubits)))

    # Measure
    counts = qiskit_measure_and_count(qc)

    res = list(counts.keys())[0][::-1]
    res_str = ""
    for qname in qf.truth_table_header()[-qf.ret_size :]:
        res_str += res[circ.qubit_map[qname]]

    cls.assertEqual(len(counts), 1)

    max_qubits = (
        qf.input_size
        + len(qf.expressions)
        + sum([gateinputcount(compiler.optimizer(e[1])) for e in qf.expressions])
    )

    cls.assertLessEqual(qf.gate().num_qubits, max_qubits)

    return res_str


def compute_result_of_originalf(cls, qf, truth_line):
    """Compute the result of originalf for a given truth_line containing inputs"""

    def truth_to_arg(truth, i, argtt):
        """Translate a bin string truth starting from i, to type argtt"""
        if argtt == bool:
            return truth[i], i + 1
        elif inspect.isclass(argtt) and issubclass(argtt, Qtype):
            return (
                argtt.from_bool(truth[i : i + argtt.BIT_SIZE]),
                i + argtt.BIT_SIZE,
            )
        else:  # A tuple
            al = []
            for x in get_args(argtt):
                a, i = truth_to_arg(truth, i, x)
                al.append(a)
            return tuple(al), i

    def res_to_str(res):
        """Translate res to a binary string"""
        if type(res) == bool:
            return "1" if res else "0"
        elif type(res) == tuple:
            return "".join([res_to_str(x) for x in res])
        else:
            return res.to_bool_str()

    args = []
    i = 0
    for x in qf.args:
        arg, i = truth_to_arg(truth_line, i, x.ttype)
        args.append(arg)

    cls.assertEqual(i, qf.input_size)

    res_original = qf.original_f(*args)
    res_original_str = res_to_str(res_original)

    cls.assertEqual(len(res_original_str), qf.ret_size)
    return res_original_str


def compute_and_compare_results(cls, qf):
    """Create and simulate the qcircuit, and compare the result with the
    truthtable and with the original_f"""
    truth_table = qf.truth_table()

    for truth_line in truth_table:
        # Extract str of truthtable and result
        truth_str = "".join(
            map(lambda x: "1" if x else "0", truth_line[-qf.ret_size :])
        )

        # Calculate and compare the gate result
        if COMPILATION_ENABLED:
            res_qc = compute_result_of_qcircuit(cls, qf, truth_line)
            cls.assertEqual(truth_str, res_qc)

        # Calculate and compare the originalf result
        res_original = compute_result_of_originalf(cls, qf, truth_line)
        cls.assertEqual(truth_str, res_original)
