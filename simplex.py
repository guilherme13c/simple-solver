from simplex_tableau import *

# TODO: Fix simplex loop
def simplex(tableau):
    lines = len(tableau)
    cols = len(tableau[0])
    
    status = ""
    certificate = []
    
    run = True
    while run == True:
        pivot_col = find_pivot_col(tableau)
        if pivot_col == None:
            run = False
            status = "optimal"
            return
        
        pivot_row = find_pivot_row(tableau, pivot_col)
        if pivot_row == None:
            run = False
            status = "infeasible"
            return
        
        tableu = pivot(tableau, pivot_col, pivot_row)
    
    return tableu, status, certificate
    

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
    for i in range(lines, cols-1):
        if min_so_far > tableau[0,i]:
            min_idx = i
            min_so_far = tableau[0,min_idx]
    
    return min_idx

def find_pivot_row(tableau, col):
    last_col = [i for i in tableau[1:,-1]]
    pivot_col = [i for i in tableau[1:,col]]
    
    aux_col = []
    for i in range(len(last_col)):
        aux_col.append(sp.parse_expr(f"{last_col[i]}/{pivot_col[i]}"))
    
    min_so_far = 0
    min_idx = None
    for i in range(len(aux_col)):
        if aux_col[min_so_far] > aux_col[i]:
            min_idx = i
            min_so_far = aux_col[min_idx]
    
    if min_idx == None: return None        
    else: return min_idx+1

def pivot(tableau, pivot_col, pivot_row):
    lines = len(tableau)
    cols = len(tableau[0])
    
    pivot_element = sp.parse_expr(tableau[pivot_row,pivot_col])
    
    for i in range(cols):
        tableau[i,pivot_col] = tableau[i,pivot_col]/pivot_element
    
    for i in range(lines):
        multiple = sp.parse_expr(f"{tableau[i,pivot_col]} / {pivot_element}")
        
        for j in range(cols):
            if j != pivot_col:
                tableau[i,j] = tableau[i,j] - multiple*tableau[i,j]
                
    return tableau

