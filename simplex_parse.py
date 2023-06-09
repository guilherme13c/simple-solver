import sympy as sp
from typing import Union, List

MAX = "MAX"
MIN = "MIN"

def parse_objective_function(optimization: Union[MAX, MIN], expr: str):
    if (optimization == MIN):
        expr = -sp.parse_expr(expr)
    
    elif (optimization == MAX):
        expr = sp.parse_expr(expr)

    return MAX, str(expr)

def ensure_rhs_positivity(expr: str):
    if "==" in expr:
        expr = expr.split("==")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        if rhs < 0:
            return f"{-lhs} == {-rhs}"
        else: 
            return f"{lhs} == {rhs}"
        
    elif "<=" in expr:
        expr = expr.split("<=")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        if rhs < 0:
            return f"{-lhs} >= {-rhs}"
        else: 
            return f"{lhs} <= {rhs}"
        
    elif ">=" in expr:
        expr = expr.split(">=")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        if rhs < 0:
            return f"{-lhs} <= {-rhs}"
        else: 
            return f"{lhs} >= {rhs}"
    
    else: 
        return expr

def extract_variables(expr: str):
    variables = set()
    if "==" in expr:
        expr = expr.split("==")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        for v in lhs.free_symbols.union(rhs.free_symbols):
            variables.add(v)
            
    elif "<=" in expr:
        expr = expr.split("<=")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        for v in lhs.free_symbols.union(rhs.free_symbols):
            variables.add(v)
            
    elif ">=" in expr:
        expr = expr.split(">=")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        for v in lhs.free_symbols.union(rhs.free_symbols):
            variables.add(v)

    else:
        try:
            expr = sp.parse_expr(expr)
            for v in expr.free_symbols:
                variables.add(v)
        except:
            raise Exception
            
    return variables

def is_non_negativity_constraint_for(constraint: str, variable: str):
    if not ">=" in constraint or not variable in constraint:
        return False
    
    expr = constraint.split(">=")
    lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
    
    if len(lhs.free_symbols) != 1:
        return False
    if rhs < 0:
        return False

    return True

def add_slack_variables(constraints: List[str]):
    slack_variables = set()
    
    for i in range(len(constraints)):
        if "==" in constraints[i]:
            continue
        
        elif "<=" in constraints[i]:
            constraints[i] = constraints[i].replace("<=", f"+ s{i+1} ==")
            slack_variables.add(f"s{i+1}")
            
        elif ">=" in constraints[i]:
            expr = constraints[i].split(">=")
            lhs = sp.parse_expr(expr[0])
            rhs = sp.parse_expr(expr[1])
            if not(len(lhs.free_symbols) == 1 and rhs == 0):
            
                constraints[i] = constraints[i].replace(">=", f"- s{i+1} ==")
                slack_variables.add(f"s{i+1}")
            
    return sorted(list(slack_variables)), constraints

def add_additional_variables(constraints: List[str]):
    additional_variables = set()
    
    for i in range(len(constraints)):
        if "==" in constraints[i]:
            constraints[i] = constraints[i].replace("==", f"+ u{i+1} ==")
            additional_variables.add(f"u{i+1}")
            
    return sorted(list(additional_variables)), constraints

def add_slack_and_additional_variables(constraints: List[str]):
    slack_variables = set()
    additional_variables = set()

    for i in range(len(constraints)):
        if "==" in constraints[i]:
            constraints[i] = constraints[i].replace("==", f"+ u{i+1} ==")
            additional_variables.add(f"u{i+1}")
        
        elif "<=" in constraints[i]:
            constraints[i] = constraints[i].replace("<=", f"+ s{i+1} ==")
            slack_variables.add(f"s{i+1}")
            
        elif ">=" in constraints[i]:
            if not is_non_negativity_constraint(constraints[i]):
                constraints[i] = constraints[i].replace(">=", f"- s{i+1} + u{i+1} ==")
                slack_variables.add(f"s{i+1}")
                additional_variables.add(f"u{i+1}")
                
    return sorted(list(additional_variables)), sorted(list(slack_variables)), constraints

def is_non_negativity_constraint(constraint: str):
    if not ">=" in constraint:
        return False
    
    expr = constraint.split(">=")
    lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
    
    if len(lhs.free_symbols) != 1:
        return False
    if rhs != 0:
        return False

    return True

def extract_objective_coefficients(objective: str, variables: List[str]):
    tmp_coef_dict = dict(sp.parse_expr(objective).as_coefficients_dict())
    coef_dict = dict()
    for i in tmp_coef_dict.keys():
        coef_dict[i.name] = tmp_coef_dict[i]
        
    coefs = []
    for i in range(len(variables)):
        if variables[i] in coef_dict.keys():
            coefs.append(coef_dict[variables[i]])
        else:
            coefs.append(0)
    return coefs

def extract_constraints_coefficients(constraints: List[str], variables: List[str]):
    b = []
    a = []
    
    for constraint in constraints:
        if is_non_negativity_constraint(constraint): continue
        expr = constraint.split("==")
        lhs, rhs = sp.parse_expr(expr[0]), sp.parse_expr(expr[1])
        tmp_lhs_coef_dict = lhs.as_coefficients_dict()
        lhs_coef_dict = dict()
        for i in tmp_lhs_coef_dict.keys():
            lhs_coef_dict[i.name] = tmp_lhs_coef_dict[i]
            
        lhs_coefs = []
        for i in range(len(variables)):
            if variables[i] in lhs_coef_dict.keys():
                lhs_coefs.append(lhs_coef_dict[variables[i]])
            else:
                lhs_coefs.append(0)
                
        a.append(lhs_coefs)
        
        b.append(rhs)
        
    return a, b

        
