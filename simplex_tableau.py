from simplex_parse import *
import numpy as np

def to_tableau(objective, 
               constraints, 
               variables_after_substitution, 
               slack_variables, 
               additional_variables):
    
    lines = len([i for i in constraints if not is_non_negativity_constraint(i)])+1
    columns = lines+len(variables_after_substitution)+len(slack_variables)+len(additional_variables)
    
    tableau = np.zeros(shape=[lines, columns], dtype=sp.Expr)
    
    all_variables = []
    for i in variables_after_substitution:
        all_variables.append(i)
    for i in slack_variables:
        all_variables.append(i)
    for i in additional_variables:
        all_variables.append(i)
    
    for i in range(lines-1):
        tableau[i+1,i] = 1
    
    objective_coefs = extract_objective_coefficients(objective, all_variables)
    
    for i in range(len(objective_coefs)):
        tableau[0,lines+i-1] = -objective_coefs[i]
        
    constraint_coefficients, b = extract_constraints_coefficients(constraints, all_variables)
    
    for i in range(len(constraint_coefficients)):
        for j in range(len(constraint_coefficients[0])):
            tableau[i+1,lines+j-1] = constraint_coefficients[i][j]
        
    for i in range(len(b)):
        tableau[i+1,-1] = b[i]
        
    return tableau

def has_basic_variables(tableau):
    has = True
    lines = len(tableau)
    cols = len(tableau[0])
    
    for i in range(1,lines):
        line_has = False
        for j in range(lines, cols):
            if tableau[i,j] == 1 and all([tableau[k,j] == 0 for k in range(0,lines) if k != i]):
                line_has = True
        has = has and line_has
        
    return has

def find_cols_to_fix(tableau):
    cols_to_fix = []
    lines = len(tableau)
    cols = len(tableau[0])
    
    for i in range(1,lines):
        for j in range(lines, cols):
            if tableau[i,j] == 1 and all([tableau[k,j] == 0 for k in range(1,lines) if k != i]):
                cols_to_fix.append(j)
                
    return cols_to_fix    

def fix_col(tableau, col):
    lines = len(tableau)
    cols = len(tableau[0])
    
    line = 0
    for i in range(1, lines):
        if tableau[i,col] == 1:
            line = i

    multiple = sp.parse_expr(f"{tableau[0,col]} / {tableau[line,col]}")
    for i in range(cols):
        tableau[0,i] = tableau[0,i] - multiple*tableau[line,i]

    return tableau

def normalize_tableau(tableau):
    if has_basic_variables(tableau):
        return tableau
    
    cols_to_fix = find_cols_to_fix(tableau)
    for i in cols_to_fix:
        tableau = fix_col(tableau, i)
    
    return tableau
