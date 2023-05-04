from simplex_tableau import *

def simplex(tableau):
    lines = len(tableau)
    cols = len(tableau[0])

    while True:
        pivot_col = find_pivot_col(tableau)
        if pivot_col == None:
            status = "optimal"
            return status, tableau, [i for i in tableau[0,:lines-1]]
        
        pivot_row = find_pivot_row(tableau, pivot_col)
        if pivot_row == None:
            status = "unbounded"
            certificate = []
            for i in range(lines):
                certificate.append(tableau[i,pivot_col])

            return status, tableau, certificate

        tableau = pivot(tableau, pivot_col, pivot_row)   

def generate_auxiliar_problem(objective_function, 
                              constraints, 
                              variables_after_substitution, 
                              slack_variables, 
                              additional_variables):
    
    new_objective_function = ""
    for i in additional_variables:
        new_objective_function += f"-{i}"
    
    return new_objective_function, constraints, variables_after_substitution, slack_variables, additional_variables

def find_pivot_col(tableau):
    lines = len(tableau)
    cols = len(tableau[0])
    
    min_so_far = 0
    min_idx = None
    for i in range(lines-1, cols-1):
        if min_so_far > tableau[0,i]:
            min_idx = i
            min_so_far = tableau[0,min_idx]
    
    return min_idx

def find_pivot_row(tableau, col):
    last_col = [i for i in tableau[1:,-1]]
    pivot_col = [i for i in tableau[1:,col]]
    
    aux_col = []
    for i in range(len(last_col)):
        if pivot_col[i] > 0:
            aux_col.append(sp.parse_expr(f"{last_col[i]}/{pivot_col[i]}"))
        else:
            aux_col.append(float("inf"))

    min_so_far = float("inf")
    min_idx = None
    for i in range(len(aux_col)):
        if min_so_far > aux_col[i]:
            min_idx = i
            min_so_far = aux_col[min_idx]
    
    if min_idx == None: return None        
    else: return min_idx+1

def pivot(tableau, pivot_col, pivot_row):
    lines = len(tableau)
    cols = len(tableau[0])
    
    pivot_element = tableau[pivot_row,pivot_col]
    
    for i in range(cols):
        tableau[pivot_row,i] = tableau[pivot_row,i]/pivot_element
    
    for i in range(lines):
        if i != pivot_row:
            multiple = sp.parse_expr(f"{tableau[i,pivot_col]} / {pivot_element}")
            
            for j in range(cols):
                tableau[i,j] = tableau[i,j] - multiple*tableau[pivot_row,j]
                
    return tableau

