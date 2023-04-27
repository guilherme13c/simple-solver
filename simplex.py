import numpy as np
import sympy as sp

SYMPLEX_MAX = False
SYMPLEX_MIN = True


class SymplexInvalidExpr(Exception):
    pass


class Model:
    def __init__(self) -> None:
        self.optimization_type = SYMPLEX_MAX
        self.objective_function_expr = sp.Expr()
        self.variables = list()
        self.constraints = list()
        self.non_negative_constraints = list()

    @staticmethod
    def generate_symbolic_expr(expr: str):
        r = sp.parse_expr(expr)
        # print(r, type(r))
        # if (type(r) == bool):
        #     s = expr.split("==")
        #     lhs, rhs = s[0], s[1]
        #     r = sp.core.relational.Eq(lhs, rhs)
        return r

    def variable(self, symbol: sp.Symbol):
        self.variables.append(symbol)

    def objective_function(self, max_or_min: bool, function: sp.Expr):
        self.objective_function_expr = function
        self.optimization_type = max_or_min

    def constraint(self, constraint: sp.Expr):
        if (len(constraint.free_symbols) == 1):
            self.non_negative_constraints.append(constraint)
        else:
            self.constraints.append(constraint)

    # TODO: finish implementing
    def to_standard_form(self):
        standard_model = Model()

        # min f(X) ? max -f(X) : 0
        if self.optimization_type == SYMPLEX_MIN:
            standard_model.objective_function(
                SYMPLEX_MAX, -self.objective_function_expr)
        else:
            standard_model.objective_function(
                SYMPLEX_MAX, self.objective_function_expr)

        for v in standard_model.objective_function_expr.free_symbols:
            standard_model.variable(v)

        # y >= K ? -y <= -K : 0
        for i in range(len(self.constraints)):
            new_c = 0
            c = self.constraints[i]

            if c.has(sp.core.relational.Ge):
                new_c = -c.lhs <= -c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        # non-negative constraints correction
        # if variable xi is not positive, substitute by xi_ - xi__
        for v in self.variables:
            positive = False
            for c in self.non_negative_constraints:
                if c.has(v):
                    positive = True
        if not positive:
            self.substitute(v)

        for i in range(len(self.non_negative_constraints)):
            new_c = 0
            c = self.non_negative_constraints[i]

            if c.has(sp.core.relational.Le):
                new_c = - c.lhs >= - c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

    def show(self):
        if self.optimization_type:
            print("MIN")
        elif not (self.optimization_type):
            print("MAX")
        else:
            raise SymplexInvalidExpr

        print("Objective: \t", self.objective_function_expr)
        print("Variables: \t", self.variables)
        print("Constraints: ")
        for i in self.constraints:
            print("\t\t", i)
        print("Non-negative Constraints: ")
        for i in self.non_negative_constraints:
            print("\t\t", i)

    def substitute(self, v):
        v_ = sp.Symbol(f"{v.name}_")
        v__ = sp.Symbol(f"{v.name}__")
        print("substitution of ", v, " by ", v_, v__)

        for i in range(len(self.constraints)):
            c = self.constraints[i]
            c = c.subs(v, v_-v__)

        self.objective_function_expr = self.objective_function_expr.subs(
            v, v_-v__)

        self.variables.remove(v)
        self.variable(v_)
        self.variable(v__)

        for i in range(len(self.non_negative_constraints)):
            c = self.non_negative_constraints[i]
            if c.has(v):
                self.non_negative_constraints.remove(c)
                self.constraint(c.subs(v, v_-v__))
        self.non_negative_constraints.append(v_ >= 0)
        self.non_negative_constraints.append(v__ >= 0)


def index_min(l) -> int:
    r = 0
    for i in range(1, len(l)):
        if l[i] < l[r]:
            r = i


def initialize_simplex(model: Model):
    pass
