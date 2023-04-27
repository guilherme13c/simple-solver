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
        self.variables = set()
        self.constraints = list()

    @staticmethod
    def generate_symbolic_expr(expr: str):
        return sp.parse_expr(expr)
    
    def variable(self, symbol: sp.Symbol):
        self.variables.add(symbol)
        
    def objective_function(self, max_or_min: bool, function: sp.Expr):
        self.objective_function_expr = function
        self.optimization_type = max_or_min
        
    def constraint(self, constraint: sp.Expr):
        if (constraint.has(sp.core.relational.Ge)):
            lhs = constraint.lhs
            rhs = constraint.rhs
            lhs = (-1) * lhs
            rhs = (-1) * rhs
            constraint = sp.core.relational.Le(lhs, rhs)
        self.constraints.append(constraint)
        
    def show(self):
        print("Objective: \t", self.objective_function_expr)
        print("Variables: \t", self.variables)
        print("Constraints: ")
        for i in self.constraints:
            print("\t\t",i)
