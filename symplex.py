import numpy as np
import sympy as sp
import re

SYMPLEX_MAX = False
SYMPLEX_MIN = True

class SymplexExecutionError(Exception):
    pass

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

        # y >= K ? -y <= -K : 0
        for i in range(len(self.constraints)):
            new_c = 0
            c = self.constraints[i]

            if c.has(sp.core.relational.Ge):
                new_c = -c.lhs <= -c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)
            
        for v in standard_model.objective_function_expr.free_symbols:
            standard_model.variable(v)

        for i in range(len(self.non_negative_constraints)):
            new_c = 0
            c = self.non_negative_constraints[i]

            if c.has(sp.core.relational.Le):
                new_c = - c.lhs >= - c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        # non-negative constraints correction
        # if variable xi is not positive, substitute by xi_ - xi__
        tmp = self
        for v in self.variables:
            positive = False
            for c in self.non_negative_constraints:
                if c.has(v):
                    positive = True
            if not positive:
                tmp = self.substitute(v)

        # min f(X) ? max -f(X) : 0
        standard_model.optimization_type = SYMPLEX_MAX

        if tmp.optimization_type == SYMPLEX_MIN:
            standard_model.objective_function(
                SYMPLEX_MAX, -tmp.objective_function_expr)

        else:
            standard_model.objective_function(
                SYMPLEX_MAX, tmp.objective_function_expr)

        

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
        new = Model()
        
        _v = sp.Symbol(f"_{v.name}")
        __v = sp.Symbol(f"__{v.name}")

        for i in range(len(self.constraints)):
            c = self.constraints[i]
            c = c.subs(v, _v-__v)

        new_of = self.objective_function_expr.subs(
            v, _v-__v)
        
        new.objective_function(SYMPLEX_MAX, new_of)

        vs = self.variables
        vs.remove(v)
        new.variables = vs
        new.variable(_v)
        new.variable(__v)

        new_non_negative_constraints = self.non_negative_constraints
        for i in range(len(new_non_negative_constraints)):
            c = new_non_negative_constraints[i]
            if c.has(v):
                new_non_negative_constraints.remove(c)
                new.constraint(c.subs(v, _v-__v))
        new_non_negative_constraints.append(_v >= 0)
        new_non_negative_constraints.append(__v >= 0)
        
        new.non_negative_constraints = new_non_negative_constraints
        
        return new

    def equations(self):
        r = []
        r.append(self.objective_function_expr)
        for c in self.constraints:
            r.append(c)
        for c in self.non_negative_constraints:
            r.append(c)
        return r

    def to_slack_form(self):
        
        # N, B
        slack_model = SlackForm()
        next_var_name = max([int(re.search(r"\d+", v.name).group()) for v in self.variables]) + 1
        for v in self.constraints:
            slack_model.B.append(sp.Symbol(f"x{next_var_name}"))
            next_var_name += 1
        for v in self.variables:
            slack_model.N.append(v)

        # v
        of_const = []
        for t in self.objective_function_expr.args:
            if not t.free_symbols:
                of_const.append(t)        
        if len(of_const) == 0:
            slack_model.v = 0
        elif len(of_const) == 1:
            slack_model.v = of_const[0]
        else:
            raise SymplexExecutionError

        # b
        c_const = []
        for c in self.constraints:
            tmp = [t for t in c.args if not t.free_symbols]
            if len(tmp) == 0:
                c_const.append(0)
            elif len(tmp) == 1:
                c_const.append(tmp[0])
            else:
                raise SymplexExecutionError
        slack_model.b = c_const

        # c
        of_coef = []
        for v in self.variables:
            of_coef.append(0)
        for t in self.objective_function_expr.args:
            if t.free_symbols:
                for v in self.variables:
                    if v in t.free_symbols:
                        v_index = self.variables.index(v)
                        coef = t.args[0]
                        of_coef[v_index] = coef
        slack_model.c = of_coef
                        
        # TODO: generate A
        
        # A
        coef_matrix = []
        
        return slack_model


# def to_standard_form(model):
#     standard_model = Model()

#     # y >= K ? -y <= -K : 0
#     for i in range(len(model.constraints)):
#         new_c = 0
#         c = model.constraints[i]

#         if c.has(sp.core.relational.Ge):
#             new_c = -c.lhs <= -c.rhs
#         else:
#             new_c = c
#         standard_model.constraint(new_c)

#     # non-negative constraints correction
#     # if variable xi is not positive, substitute by xi_ - xi__
#     for v in model.variables:
#         positive = False
#         for c in model.non_negative_constraints:
#             if c.has(v):
#                 positive = True
#         if not positive:
#             tmp = model.substitute(v)
    
#     # min f(X) ? max -f(X) : 0
#     standard_model.optimization_type = SYMPLEX_MAX

#     if tmp.optimization_type == SYMPLEX_MIN:
#         standard_model.objective_function(
#             SYMPLEX_MAX, -tmp.objective_function_expr)

#     else:
#         standard_model.objective_function(
#             SYMPLEX_MAX, tmp.objective_function_expr)

#     for v in standard_model.objective_function_expr.free_symbols:
#         standard_model.variable(v)
    

#     for i in range(len(model.non_negative_constraints)):
#         new_c = 0
#         c = model.non_negative_constraints[i]

#         if c.has(sp.core.relational.Le):
#             new_c = - c.lhs >= - c.rhs
#         else:
#             new_c = c
#         standard_model.constraint(new_c)

#     standard_model.variables = model.variables

#     return standard_model

def index_min(l) -> int:
    r = 0
    for i in range(1, len(l)):
        if l[i] < l[r]:
            r = i


def initialize_simplex(model: Model):
    pass

class SlackForm:
    def __init__(self):
        self.N = []
        self.B = []
        self.A = []
        self.b = []
        self.c = []
        self.v = 0