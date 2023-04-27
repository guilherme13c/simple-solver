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
        if (type(r) == bool):
            s = expr.replace("\n", "").split("==")
            lhs, rhs = sp.parse_expr(s[0]), sp.parse_expr(s[1])
            r = [lhs >= rhs, lhs <= rhs]
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

        standard_model.variables = self.variables

        return standard_model

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
        _v = sp.Symbol(f"_{v.name}")
        __v = sp.Symbol(f"__{v.name}")
        # print("substitution of ", v, " by ", _v, __v)

        for i in range(len(self.constraints)):
            c = self.constraints[i]
            c = c.subs(v, _v-__v)

        self.objective_function_expr = self.objective_function_expr.subs(
            v, _v-__v)

        vs = self.variables
        vs.remove(v)
        self.variables = vs
        self.variable(_v)
        self.variable(__v)

        for i in range(len(self.non_negative_constraints)):
            c = self.non_negative_constraints[i]
            if c.has(v):
                self.non_negative_constraints.remove(c)
                self.constraint(c.subs(v, _v-__v))
        self.non_negative_constraints.append(_v >= 0)
        self.non_negative_constraints.append(__v >= 0)

    def equations(self):
        r = []
        r.append(self.objective_function_expr)
        for c in self.constraints:
            r.append(c)
        for c in self.non_negative_constraints:
            r.append(c)
        return r

    def to_matrix(self):
        pass


def index_min(l) -> int:
    r = 0
    for i in range(1, len(l)):
        if l[i] < l[r]:
            r = i


def initialize_simplex(model: Model):
    pass
