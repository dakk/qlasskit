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

# import os
import sys
import unittest

from qlasskit import qlassf
from qlasskit.bqm import decode_samples

# pyqubo doesn't work on python 3.12
DISABLE_BQM_TESTS = False

# os.getenv("GITHUB_ACTIONS") and
if sys.version_info.major == 3 and sys.version_info.minor == 12:
    try:
        import dimod
        import neal
    except:
        DISABLE_BQM_TESTS = True
else:
    import dimod
    import neal


def sample_bqm(bqm, reads=10):
    sa = neal.SimulatedAnnealingSampler()
    sampleset = sa.sample(bqm, num_reads=reads)
    return sampleset
    # best_sample = min(decoded_samples, key=lambda x: x.energy)


def sample_qubo(qubo):
    return dimod.ExactSolver().sample_qubo(qubo)


class TestQlassfToBQM(unittest.TestCase):
    def setUp(self):
        if DISABLE_BQM_TESTS:
            self.skipTest("Skipping this test")

    def test_to_bqm_1(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"], True)

    def test_to_bqm_2(self):
        f = "def test(a: Qint[2]) -> bool:\n\treturn a != 2"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"], 2)

    def test_to_bqm_3(self):
        f = "def test(a: Qint[2]) -> Qint[2]:\n\treturn a + 1"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"] + 1 % 16, 0)

    def test_to_bqm_4(self):
        f = "def test(a: Qint[2], b: Qint[2]) -> Qint[4]:\n\treturn Qint4(0) + a + b"
        qf = qlassf(f, to_compile=False)
        qubo, offset = qf.to_bqm("qubo")
        ss = sample_qubo(qubo)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"] + x.sample["b"] % 16, 0)

        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"] + x.sample["b"] % 16, 0)

    def test_to_bqm_subset_sum_problem(self):
        lst = [0, 5, 2, 3]
        f = (
            f"def subset_sum(ii: Tuple[Qint[2], Qint[2]]) -> Qint[3]:\n\tl = {lst}\n\t"
            "return l[ii[0]] + l[ii[1]] - 7"
        )
        qf = qlassf(f, to_compile=False)

        qubo, offset = qf.to_bqm("qubo")
        ss = sample_qubo(qubo)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(sum(map(lambda i: lst[i], x.sample["ii"])), 7)

        bqm = qf.to_bqm()
        ss = sample_bqm(bqm)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(sum(map(lambda i: lst[i], x.sample["ii"])), 7)

    def test_to_bqm_addends(self):
        f = "def test(a: Qint[4], b: Qint[4]) -> Qint[4]:\n\treturn a + b - 12"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()

        ss = sample_bqm(bqm, 100)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"] + x.sample["b"], 12)

    def test_to_bqm_factoring(self):
        f = "def test(a: Qint[3], b: Qint[3]) -> Qint[4]:\n\treturn Qint4(15) - (a * b)"
        qf = qlassf(f, to_compile=False)
        bqm = qf.to_bqm()

        ss = sample_bqm(bqm, 100)
        ds = decode_samples(qf, ss)

        filtered = list(filter(lambda x: x.energy == 0.0, ds))
        self.assertTrue(len(filtered) > 0)
        for x in filtered:
            self.assertEqual(x.sample["a"] * x.sample["b"], 15)


# class TestQlassfToBQMSamples(unittest.TestCase):
#     def test_to_bqm_samples_1(self):
