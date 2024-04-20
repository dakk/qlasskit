# Copyright 2023-204 Davide Gessa

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

from qlasskit.tools import utils

dummy = """
from qlasskit import qlassf

@qlassf
def a(b: bool) -> bool:
    return not b

@qlassf
def c(b: bool) -> bool:
    return b
"""


class TestTools_utils(unittest.TestCase):
    def test_parse_str(self):
        print(utils.parse_str(dummy))
