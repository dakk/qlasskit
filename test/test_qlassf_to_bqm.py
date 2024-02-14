# Copyright 2023-2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import dimod
import neal

from qlasskit import qlassf
from qlasskit.bqm import decode_samples


def sample_bqm(bqm, reads=10):
    sa = neal.SimulatedAnnealingSampler()
    sampleset = sa.sample(bqm, num_reads=reads)
    return sampleset
    # best_sample = min(decoded_samples, key=lambda x: x.energy)


def sample_qubo(qubo):
    return dimod.ExactSolver().sample_qubo(qubo)


class TestQlassfToBQM(unittest.TestCase):
    def test_to_bqm_1(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)
        print(ss, ds)

    def test_to_bqm_2(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a != 2"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)
        print(ss, ds)

    def test_to_bqm_3(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn a + 1"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)
        print(ss, ds)

    def test_to_bqm_4(self):
        f = "def test(a: Qint4) -> Qint4:\n\treturn a + 2"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)
        print(ss, ds)

    def test_to_bqm_5(self):
        f = "def test(a: Qint2, b: Qint2) -> Qint4:\n\treturn Qint4(0) + a + b"
        qf = qlassf(f, to_compile=False)
        qubo, offset = qf.to_bqm("qubo")
        ss = sample_qubo(qubo)
        ds = decode_samples(qf, ss)
        print("\n".join(map(str, reversed(ds))))

        print()
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)
        print("\n".join(map(str, ds)))

    def test_to_bqm_subset_sum_problem(self):
        f = (
            "def subset_sum(ii: Tuple[Qint2, Qint2]) -> Qint3:\n\tl = [0, 5, 2, 3]\n\t"
            "return l[ii[0]] + l[ii[1]] - 7"
        )
        qf = qlassf(f, to_compile=False)
        qubo, offset = qf.to_bqm("qubo")
        ss = sample_qubo(qubo)
        ds = decode_samples(qf, ss)
        print("\n".join(map(str, reversed(ds))))

        print()
        bqm = qf.to_bqm()
        print(bqm.num_variables, bqm.num_interactions)
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)
        print("\n".join(map(str, ds)))

    def test_to_bqm_factoring(self):
        f = "def test(a: Qint3, b: Qint3) -> bool:\n\treturn Qint3(3) != a * b"
        qf = qlassf(f, to_compile=False)
        # qubo, offset = qf.to_bqm('qubo')
        # ss = sample_qubo(qubo)
        # ds = decode_samples(qf, ss)
        # print('\n'.join(map(str, reversed(ds))))
        # print()
        print(qf.expressions)

        bqm = qf.to_bqm()

        print(bqm.num_variables, bqm.num_interactions)

        ss = sample_bqm(bqm, 100)
        ds = decode_samples(qf, ss)
        print("\n".join(map(str, ds)))


# class TestQlassfToBQMSamples(unittest.TestCase):
#     def test_to_bqm_samples_1(self):
