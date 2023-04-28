from __future__ import print_function
import builtins as __builtin__

import numpy as np
import sympy as sp

SYMPLEX_MAX = False
SYMPLEX_MIN = True

SYMPLEX_ZERO = 1e-9

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

        # y >= K ? -y <= -K : 0
        for i in range(len(tmp.constraints)):
            new_c = 0
            c = tmp.constraints[i]

            if c.has(sp.core.relational.Ge):
                new_c = -c.lhs <= -c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        for i in range(len(tmp.non_negative_constraints)):
            new_c = 0
            c = tmp.non_negative_constraints[i]

            if c.has(sp.core.relational.Le):
                new_c = - c.lhs >= - c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        # min f(X) ? max -f(X) : 0
        standard_model.optimization_type = SYMPLEX_MAX

        if tmp.optimization_type == SYMPLEX_MIN:
            standard_model.objective_function(
                SYMPLEX_MAX, -tmp.objective_function_expr)

        else:
            standard_model.objective_function(
                SYMPLEX_MAX, tmp.objective_function_expr)

        for v in standard_model.objective_function_expr.free_symbols:
            standard_model.variable(v)

        return standard_model


    """
    generate form:
    MAX cT . x
    s.t.:
        A . x <= b
        x >= 0
    """
    def to_matrix_form(self):
        
        c = []
        x = []
        a = []
        b = []
        
        for i in range(len(self.constraints)):
            b.append(0)
        
        # Extract variables
        x = self.variables
        var_index = dict()
        for i in range(len(x)):
            c.append(0)
            a.append([])
            var_index[x[i]] = i
        
        coefficients = dict(self.objective_function_expr.as_coefficients_dict())
        
        # Extract coefficients from the objective function
        for i in range(len(x)):
            c[i] = coefficients[x[i]]
            
        # Extract coefficients from constraints
        for i in range(len(self.constraints)):
            a[i] = [0 for k in range(len(self.constraints))]
            constraint = self.constraints[i]
            coefficients = dict(constraint.lhs.as_coefficients_dict())
            b[i] = constraint.rhs
            for j in range(len(x)):
                a[i][j] = 0
                if x[j] in coefficients:
                    a[i][j] = coefficients[x[j]]
        
        return np.array(a), np.array(x), np.array(c), np.array(b)     

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
            new.constraint(c.subs(v, _v-__v))

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
        slack_model = Model()
        
        slack_model.objective_function(SYMPLEX_MAX, self.objective_function_expr)
        slack_model.variables = self.variables
        
        constraints = []
        for i in range(len(self.constraints)):
            c = self.constraints[i]
            constraints.append(Equation(c.lhs + sp.Symbol(f"s{i}"), c.rhs))
            slack_model.variable(f"s{i}")
        slack_model.constraints = constraints
        
        
        
        slack_model.show()
        
    

    def rename_variable(self, old: sp.Symbol, new: sp.Symbol) -> None:
        # rename in self.variables
        for i in range(len(self.variables)):
            if self.variables[i] == old:
                self.variables[i] = new
                
        # rename in of
        self.objective_function_expr = self.objective_function_expr.subs(old, new)
        
        # rename in constraints
        for i in range(len(self.constraints)):
            self.constraints[i] = self.constraints[i].subs(old, new)

        
        # rename in non_negative_constraints
        for i in range(len(self.non_negative_constraints)):
            self.non_negative_constraints[i] = self.non_negative_constraints[i].subs(
                old, new)

    def reset_variable_names(self):
        for i in range(len(self.variables)):
            self.rename_variable(self.variables[i], sp.Symbol(f"k{i}"))
            
        for i in range(len(self.variables)):
            self.rename_variable(sp.Symbol(f"k{i}"), sp.Symbol(f"x{i+1}"))

class Equation:
    def __init__(self, lhs:sp.Expr()=sp.Expr(), rhs:sp.Expr()=sp.Expr()) -> None:
        self.lhs : sp.Expr = lhs
        self.rhs : sp.Expr = rhs
