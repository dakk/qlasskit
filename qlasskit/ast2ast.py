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
import ast


class ASTRewriter(ast.NodeTransformer):
    def visit_Call(self, node):
        if not hasattr(node.func, "id"):
            return node

        if node.func.id == "print":
            return None

        elif node.func.id in ["min", "max"]:
            if len(node.args) == 1:
                if isinstance(node.args[0], ast.Tuple):
                    args = node.args[0].elts
                else:
                    # TODO: not handled the case when the arg is a tuple;
                    # we can infer the type, in some way
                    return node.args[0]
            else:
                args = node.args

            op = ast.Gt() if node.func.id == "max" else ast.Lt()

            def iterif(arg_l):
                if len(arg_l) == 1:
                    return arg_l[0]
                else:
                    comps = [
                        ast.Compare(left=arg_l[0], ops=[op], comparators=[l_it])
                        for l_it in arg_l[1:]
                    ]
                    comp = ast.BoolOp(op=ast.And(), values=comps)
                    return ast.IfExp(test=comp, body=arg_l[0], orelse=iterif(arg_l[1:]))

            return iterif(args)

        else:
            return node


def ast2ast(a_tree):
    new_ast = ASTRewriter().visit(a_tree)
    # print(ast.dump(new_ast))
    return new_ast
