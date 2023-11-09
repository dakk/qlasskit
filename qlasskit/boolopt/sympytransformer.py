from sympy.logic import ITE, And, Implies, Not, Or, Xor


class SympyTransformer:
    def visit(self, e):
        if isinstance(e, And):
            return self.visit_And(e)
        elif isinstance(e, Or):
            return self.visit_Or(e)
        elif isinstance(e, Not):
            return self.visit_Not(e)
        elif isinstance(e, Implies):
            return self.visit_Implies(e)
        elif isinstance(e, ITE):
            return self.visit_ITE(e)
        elif isinstance(e, Xor):
            return self.visit_Xor(e)
        else:
            return e

    def visit_And(self, e):
        return And(*[self.visit(a) for a in e.args])

    def visit_Or(self, e):
        return Or(*[self.visit(a) for a in e.args])

    def visit_Not(self, e):
        return Not(self.visit(e.args[0]))

    def visit_ITE(self, e):
        return ITE(*[self.visit(a) for a in e.args])

    def visit_Implies(self, e):
        return Implies(*[self.visit(a) for a in e.args])

    def visit_Xor(self, e):
        return Xor(*[self.visit(a) for a in e.args])
