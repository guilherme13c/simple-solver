import numpy as np
import sympy as sp

SYMPLEX_MAX = False
SYMPLEX_MIN = True

SYMPLEX_ZERO = 1e-9

class SymplexExecutionError(Exception):
    pass

class SymplexInvalidExpr(Exception):
    pass

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
    # r = 1
    # for i in range(1,len(T[0,:])-1):
    #     if T[0,i] < T[0,r]:
    #         r = i
    # if T[0,r] >= 0:
    #     return None
    # else:
    #     return r
    
    r = 1
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