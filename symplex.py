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
        self.slack_vars = list()

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
            if type(i) != Equation:
                print("\t\t", i)
            else:
                print("\t\t", i.lhs, " == ", i.rhs)
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

    def to_slack_form(self):
        slack_model = Model()
        
        slack_model.objective_function(SYMPLEX_MAX, self.objective_function_expr)
        slack_model.variables = self.variables
        
        constraints = []
        slack_model.non_negative_constraints = self.non_negative_constraints
        for i in range(len(self.constraints)):
            c = self.constraints[i]
            constraints.append(Equation(c.lhs + sp.Symbol(f"s{i}"), c.rhs))
            slack_model.variable(sp.Symbol(f"s{i}"))
            slack_model.slack_vars.append(sp.Symbol(f"s{i}"))
            slack_model.non_negative_constraints.append(sp.parse_expr(f"s{i} >= 0"))
        slack_model.constraints = constraints
        
        return slack_model
    
    def to_tableau(self):
        m, n = len(self.constraints), len(self.variables)
        A = np.zeros(shape=[m+1,n+1], dtype=sp.Expr)
        
        A[0,0] = 1
        
        for i in range(1, m+1):
            A[i,0] = 0
        
        coefs = []
        for v in self.variables:
            c = extract_coefficient(self.objective_function_expr, v)
            coefs.append(c)
        for i in range(1, n+1):
            A[0,i] = -coefs[i-1]
        
        A_tmp = [] 
        for c in self.constraints:
            coefs = []
            for v in self.variables:
                coefs.append(extract_coefficient(c.lhs, v))
            A_tmp.append(coefs)
        for i in range(1, m+1):
            for j in range(1, n+1):
                A[i,j] = A_tmp[i-1][j-1]
        
        b = [0]
        for c in self.constraints:
            b.append(c.rhs)
        b = np.array(b, dtype=sp.Expr)
        
        x = [sp.Symbol("_w")]
        for v in self.variables:
            x.append(v)
        x = np.array(x, dtype=sp.Expr)
        
        T = np.zeros(shape=[m+1,n+2], dtype=sp.Expr)
        for i in range(0,m+1):
            T[i,-1] = b[i]
            for j in range(0,n+1):
                T[i,j] = A[i,j]
                
        return T        
        
    def rename_variable(self, old: sp.Symbol, new: sp.Symbol) -> None:
        # rename in self.variables
        for i in range(len(self.variables)):
            if self.variables[i] == old:
                self.variables[i] = new
                
        # rename in of
        self.objective_function_expr = self.objective_function_expr.subs(old, new)
        
        # rename in constraints
        for i in range(len(self.constraints)):
            if type(self.constraints[i]) != Equation:
                self.constraints[i] = self.constraints[i].subs(old, new)
            else:
                self.constraints[i] = Equation(self.constraints[i].lhs.subs(old, new), self.constraints[i].rhs.subs(old, new))
        
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

def subs_vars(expr: sp.Expr, vars: list, vals: list):
    assert len(vals) == len(vars)
    
    if len(vars) > 0:
        subs_vars(expr.subs(vars[0], vals[0]), vars[1:], vals[1:])
    
def extract_coefficient(expr: sp.Expr, v):
    d = expr.as_coefficients_dict()
    if v in d:
        return d[v]
    else:
        return 0

def find_pivot_column(T: np.ndarray) -> int:
    # r = min(T[0,1:T.shape[1]])
    # r = min([r, 0])

    # return r
    
    r = 1
    for i in range(2,T.shape[1]):
        if T[0,i] < T[0,r]:
            r = i
    if T[0,r] >= 0:
        return None
    else:
        return r

def find_pivot_row(T: np.ndarray, pivot_col: int) -> int:
    last_col = T[:,-1]
    col = T[:,pivot_col]
    
    for i in range(1,T.shape[0]-1):
        if col[i] < SYMPLEX_ZERO:
            return None
        last_col[i] /= col[i]
    
    r = 1
    for i in range(2,T.shape[0]-1):
        if last_col[i] < last_col[r]:
            r = i
            
    return r

# TODO: Fix pivot
def pivot(T: np.ndarray, row: int, col: int) -> np.ndarray:
    pivot_value = T[row,col]

    if pivot_value < SYMPLEX_ZERO:
        return None
    
    for i in range(len(T[row,:])):
        T[row,i] /= pivot_value
        
    for i in range(len(T)):
        if i != row:
            multiplier = T[i,col]
            for j in range(len(T[0])):
                T[i,j] = T[i][j] - multiplier * T[row][j]
    return T
