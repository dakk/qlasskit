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
    def __init__(self, env={}, ret=None):
        self.env = {}
        self.ret = None

    def __unroll_arg(self, arg):
        if isinstance(arg, ast.Tuple):
            return arg.elts
        elif isinstance(arg, ast.Name):
            if (
                arg.id in self.env
                and isinstance(self.env[arg.id], ast.Subscript)
                and self.env[arg.id].value.id == "Tuple"
            ):
                return [
                    ast.Subscript(
                        value=ast.Name(id=arg.id, ctx=ast.Load()),
                        slice=ast.Index(value=ast.Constant(value=i, kind=None)),
                    )
                    for i in range(len(self.env[arg.id].slice.value.elts))
                ]
        return [arg]

    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_FunctionDef(self, node):
        for x in node.args.args:
            self.env[x.arg] = x.annotation
        self.ret = node.returns

        return super().generic_visit(node)

    def visit_Assign(self, node):
        was_known = node.targets[0].id in self.env

        if isinstance(node.value, ast.Name) and node.value.id in self.env:
            self.env[node.targets[0].id] = self.env[node.value.id]
        else:
            self.env[node.targets[0].id] = "Uknown"

        # TODO: support unrolling tuple
        # Reassigning an already present variable (use a temp variable)
        if was_known:
            new_targ = ast.Name(id=f"__{node.targets[0].id}", ctx=ast.Load())
            return [
                ast.Assign(
                    targets=[new_targ],
                    value=node.value,
                ),
                ast.Assign(
                    targets=node.targets,
                    value=new_targ,
                ),
            ]

        return node

    def visit_AugAssign(self, node):
        """Translate AugAssign to Assign + BinOp (+=, -=, etc)"""
        # Reassigning an already present variable (use a temp variable)
        # if node.target.id in self.env:
        new_targ = ast.Name(id=f"__{node.target.id}", ctx=ast.Load())

        return [
            ast.Assign(
                targets=[new_targ],
                value=ast.BinOp(left=node.target, op=node.op, right=node.value),
            ),
            ast.Assign(
                targets=[node.target],
                value=new_targ,
            ),
        ]

    def visit_For(self, node):
        # For(
        #     target=Name(id="x", ctx=Store()),
        #     iter=Call(
        #         func=Name(id="range", ctx=Load()),
        #         args=[Constant(value=2, kind=None)],
        #         keywords=[],
        #     ),
        #     body=[
        #         AugAssign(
        #             target=Name(id="a", ctx=Store()),
        #             op=Add(),
        #             value=Constant(value=1, kind=None),
        #         )
        #     ],
        #     orelse=[],
        #     type_comment=None,
        # )
        # print(ast.dump(node))
        return node

    def visit_Call(self, node):
        if not hasattr(node.func, "id"):
            return node

        if node.func.id == "print":
            return None

        elif node.func.id == "len":
            if len(node.args) != 1:
                raise Exception("not handled")

            args = self.__unroll_arg(node.args[0])
            return ast.Constant(value=len(args))

        elif node.func.id in ["min", "max"]:
            if len(node.args) == 1:
                args = self.__unroll_arg(node.args[0])
            else:
                args = node.args

            op = ast.Gt() if node.func.id == "max" else ast.LtE()

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
    # print(ast.dump(a_tree))
    a_tree = ASTRewriter().visit(a_tree)
    # print(ast.dump(a_tree))
    return a_tree
