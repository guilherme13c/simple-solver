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
        return sp.parse_expr(expr)

    def variable(self, symbol: sp.Symbol):
        self.variables.append(symbol)

    def objective_function(self, max_or_min: bool, function: sp.Expr):
        self.objective_function_expr = function
        self.optimization_type = max_or_min

    def constraint(self, constraint: sp.Expr):
        # if (constraint.has(sp.core.relational.Ge)):
        #     lhs = constraint.lhs
        #     rhs = constraint.rhs
        #     lhs = (-1) * lhs
        #     rhs = (-1) * rhs
        #     constraint = sp.core.relational.Le(lhs, rhs)

        if (len(constraint.lhs.free_symbols) == 1 and constraint.rhs == 0):
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

            if self.constraints[i].has(sp.core.relational.Ge):
                new_c = -self.constraints[i].lhs <= -self.constraints[i].rhs
            else:
                new_c = self.constraints[i]
            standard_model.constraint(new_c)

        for i in range(len(self.non_negative_constraints)):
            new_c = 0
            c = self.non_negative_constraints[i]

            if c.has(sp.core.relational.Ge):
                new_c = - c.lhs <= - c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        standard_model.show()

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


def index_min(l) -> int:
    r = 0
    for i in range(1, len(l)):
        if l[i] < l[r]:
            r = i


def initialize_simplex(model: Model):
    pass
