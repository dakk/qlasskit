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

from qlasskit import Qint2, Qint4, QlassF, exceptions, qlassf



class TestQlassfToBQM(unittest.TestCase):
    def test_to_bqm_1(self):
        f = "def test(a: bool) -> bool:\n\treturn not a"
        qf = qlassf(f, to_compile=False)        
        bqm = qf.to_bqm()

    def test_to_bqm_2(self):
        f = "def test(a: Qint2) -> bool:\n\treturn a == 2"
        qf = qlassf(f, to_compile=False)        
        bqm = qf.to_bqm()
        print(bqm)

    def test_to_bqm_3(self):
        f = "def test(a: Qint2) -> Qint2:\n\treturn a + 1"
        qf = qlassf(f, to_compile=False)        
        bqm = qf.to_bqm()

    def test_to_bqm_4(self):
        f = "def test(a: Qint4) -> Qint4:\n\treturn a + 2"
        qf = qlassf(f, to_compile=False)        
        bqm = qf.to_bqm()
