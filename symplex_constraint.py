from typing import Union, List
import sympy as sp
from symplex_error import *


class Constraint:
    def __init__(self, lhs: sp.Expr, rhs: sp.Expr):
        self.lhs: sp.Expr = lhs
        self.rhs: sp.Expr = rhs
        self.non_negativity: bool = False

    def __str__(self):
        if self.non_negativity:
            return f"{self.lhs} >= {self.rhs}"
        return f"{self.lhs} == {self.rhs}"

    def __hash__(self) -> int:
        return hash(self.lhs - self.rhs)

    def free_symbols(self) -> set:
        return self.lhs.free_symbols.union(self.rhs.free_symbols)

    def subs(self, old: Union[sp.Expr, sp.Symbol], new: Union[sp.Expr, sp.Symbol]):
        self.lhs, self.rhs = self.lhs.subs(old, new), self.rhs.subs(old, new)
        return self

    def has(self, v) -> bool:
        if type(self.rhs) != sp.Expr:
            return self.lhs.has(v)
        return self.lhs.has(v) or self.rhs.has(v)


def to_equality(expr: sp.Expr, new_var_name: str = "u") -> Constraint:
    if expr.has(sp.core.relational.Ge):
        expr.lhs, expr.rhs = -expr.lhs, -expr.rhs
    additional_var = sp.Symbol(new_var_name)
    return Constraint(expr.lhs + additional_var, expr.rhs)


def is_non_negativity_constraint(constraint: str) -> bool:
    idx = constraint.find(">=")
    if idx:
        sides = constraint.split(">=")
        if len(sides) != 2:
            return False
        lhs, rhs = sp.parse_expr(sides[0]), sp.parse_expr(sides[1])
        if rhs != 0 or len(lhs.free_symbols) != 1:
            return False
        return True

    else:
        return False


def parse_constraints(exprs: List[str]) -> List[Constraint]:
    constraints = list()
    count = 1

    for i in range(len(exprs)):
        expr = "".join(exprs[i])
        print(expr)

        # add auxiliar variable
        if expr.find("==") != -1:
            expr = expr.split("==")
            if len(expr) != 2:
                raise SymplexParsingFailed

            count, tmp = handle_eq(expr[0], expr[1], count)
            for j in tmp:
                constraints.append(j)

        # add negative slack and auxiliar variables
        elif expr.find(">=") != -1:
            expr = expr.split(">=")
            if len(expr) != 2:
                raise SymplexParsingFailed

            count, tmp = handle_ge(expr[0], expr[1], count)
            
            for j in tmp:
                constraints.append(j)


        # add positive slack variable
        elif expr.find("<=") != -1:
            expr = expr.split(">=")
            if len(expr) != 2:
                raise SymplexParsingFailed
            
            count, tmp = handle_le(expr[0], expr[1], count)
            
            for j in tmp:
                constraints.append(j)

        else:
            print(expr)
            raise SymplexParsingFailed

    return constraints


def parse_constraint(expr: str) -> Constraint:
    if expr.find("==") != -1:
        expr = expr.split("==")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        return Constraint(lhs, rhs)

    elif expr.find(">=") != -1:
        expr = expr.split(">=")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])

        if len(lhs.free_symbols) == 1 and rhs == 0:
            c = Constraint(lhs, rhs)
            c.non_negativity = True
            return c
        else:
            lhs, rhs = -lhs+sp.Symbol("t"), -rhs
            return Constraint(lhs, rhs)

    elif expr.find("<="):
        expr = expr.split("<=")
        lhs, rhs = sp.parse_expr(
            expr[0])+sp.Symbol("t"), sp.parse_expr(expr[1])
        return Constraint(lhs, rhs)

    else:
        raise SymplexParsingFailed

def handle_eq(lhs: str, rhs: str, count: int) -> List[Constraint]:
    lhs, rhs = sp.parse_expr(lhs[0]), sp.parse_expr(rhs[1])
    
    if rhs < 0:
        lhs, rhs = -lhs, -rhs

    c_aux = Constraint(sp.Symbol(f"u{count}"), 0)
    c_aux.non_negativity = True

    c = Constraint(lhs+sp.Symbol(f"u{count}"), rhs)

    count += 1

    return count, [c, c_aux]

def handle_le(lhs: str, rhs: str, count: int) -> List[Constraint]:    
    lhs, rhs = sp.parse_expr(lhs), sp.parse_expr(rhs)
    
    if rhs < 0:
        lhs, rhs = -lhs, -rhs
        return handle_ge(lhs, rhs, count)

    c_slack = Constraint(sp.Symbol(f"s{count}"), 0)
    c_slack.non_negativity = True

    c = Constraint(lhs+sp.Symbol(f"s{count}"), rhs)
    
    count += 1
    
    return count, [c, c_slack]
        
def handle_ge(lhs: str, rhs: str, count: int) -> List[Constraint]:
    lhs, rhs = sp.parse_expr(lhs), sp.parse_expr(rhs)
    
    if rhs < 0:
        lhs, rhs = -lhs, -rhs
        return handle_le(lhs, rhs, count)
    
    if rhs == 0 and len(lhs.free_symbols) == 1:
        c = Constraint(lhs, rhs)
        c.non_negativity = True
        return count, [c]
    
    c_slack = Constraint(sp.Symbol(f"s{count}"), 0)
    c_slack.non_negativity = True
    
    c_aux = Constraint(sp.Symbol(f"u{count}"), 0)
    c_aux.non_negativity = True

    c = Constraint(lhs+sp.Symbol(f"s{count}")+sp.Symbol(f"u{count}"), rhs)
    
