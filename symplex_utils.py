import numpy as np
import sympy as sp

SYMPLEX_MAX = False
SYMPLEX_MIN = True

SYMPLEX_INFEASIBLE = "inviavel"
SYMPLEX_UNBOUNDED = "ilimitado"
SYMPLEX_OPTIMAL = "otimo"

SYMPLEX_ZERO = 1e-9

class SymplexExecutionError(Exception):
    pass

class SymplexInvalidExpr(Exception):
    pass

class Equation:
    def __init__(self, lhs:sp.Expr()=sp.Expr(), rhs:sp.Expr()=sp.Expr()) -> None:
        self.lhs : sp.Expr = lhs
        self.rhs : sp.Expr = rhs
        self.free_symbols = set()
        [self.free_symbols.add(i) for i in lhs.free_symbols]
        [self.free_symbols.add(i) for i in rhs.free_symbols]

def subs_vars(expr: sp.Expr, vars: list, vals: list) -> None:
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
    for i in range(1,len(T[0,:])-1):
        if T[0,i] < 0:
            return i
    return None


def find_pivot_row(T: np.ndarray, pivot_col: int) -> int:
    last_col = list()
    col = T[:,pivot_col]
    
    for i in range(len(T[:,0])):
        if col[i] <= 0:
            last_col.append(float("inf"))
        else:
            last_col.append(T[i,-1]/col[i])
        
    r = 1
    for i in range(1,len(T[:,0])):
        if last_col[i] < last_col[r]:
            r = i
    
    if last_col[r] == float("inf"): return None
    return r

def pivot(T: np.ndarray, row: int, col: int) -> np.ndarray:
    tableau = T
    pivot_value = tableau[row,col]

    if pivot_value < SYMPLEX_ZERO and pivot_value >= 0: return None
    
    tableau[row,:] /= pivot_value
    
    for i in range(len(tableau)):
        if i != row:
            multiplier = tableau[i,col]
            for j in range(len(T[0,:])):
                tableau[i,j] = tableau[i,j] - multiplier * tableau[row,j]
                
    return tableau

def find_pivot_column_extended(T: np.ndarray, R: int, V: int) -> int:    
    for i in range(R,R+V):
        if T[0,i] < 0:
            return i
    return None

def find_pivot_row_extended(T: np.ndarray, pivot_col: int, R: int, V: int) -> int:
    last_col = list()
    col = T[:,pivot_col]
    
    for i in range(len(T[:,0])):
        if col[i] <= 0:
            last_col.append(float("inf"))
        else:
            last_col.append(T[i,-1]/col[i])
        
    r = 1
    for i in range(1,len(T[:,0])):
        if last_col[i] < last_col[r]:
            r = i
    
    return r

def pivot_extended(T: np.ndarray, row: int, col: int, R: int, V: int) -> np.ndarray:
    tableau = T
    pivot_value = tableau[row,col]

    if pivot_value < SYMPLEX_ZERO and pivot_value >= 0: return None
    
    tableau[row,:] /= pivot_value
    
    for i in range(len(tableau)):
        if i != row:
            multiplier = tableau[i,col]
            for j in range(len(T[0,:])):
                tableau[i,j] = tableau[i,j] - multiplier * tableau[row,j]
                
    return tableau

def generate_symbolic_expr(expr: str):
    r = sp.parse_expr(expr)
    if (type(r) == bool):
        s = expr.replace("\n", "").split("==")
        lhs, rhs = sp.parse_expr(s[0]), sp.parse_expr(s[1])
        r = [lhs >= rhs, lhs <= rhs]
    return r
