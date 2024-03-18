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
from . import TExp, _eq, _neq


class Qbool:
    @staticmethod
    def eq(tleft: TExp, tcomp: TExp) -> TExp:
        return (tleft[0], _eq(tleft[1], tcomp[1]))

    @staticmethod
    def neq(tleft: TExp, tcomp: TExp) -> TExp:
        return (tleft[0], _neq(tleft[1], tcomp[1]))
