import sys
from symplex_model_v1 import *
from read_input import read_input

def symplex(max_or_min, obj_function, constraints):
    model = Model()

    variables = obj_function.free_symbols
    for v in variables:
        model.variable(v)

    model.objective_function(max_or_min, obj_function)

    for c in constraints:
        model.constraint(c)


    sp.init_printing(use_unicode=True, use_latex=True)
    

    standard_model = model.to_standard_form()
    standard_model.reset_variable_names()

    slack_model = standard_model.to_slack_form()
    
    T = slack_model.to_tableau()

    found = False
    while not found:
        col = find_pivot_column(T)
        if col == None:
            found = True
            continue
        row = find_pivot_row(T, col)
        if row == None:
            found = True
            continue
        T = pivot(T, row, col)

def two_phase_symplex(max_or_min, obj_function, constraints):
    model = Model()

    variables = obj_function.free_symbols
    for v in variables:
        model.variable(v)

    model.objective_function(max_or_min, obj_function)

    for c in constraints:
        model.constraint(c)
        
    model.show()
    print("----------------------------------------------------------")
        
    standard_model = model.to_standard_form()
    standard_model.show()
    print("----------------------------------------------------------")
    
    aux_problem = standard_model.generate_aux_problem()
    
    aux_problem.show()
    print("----------------------------------------------------------")
    
    T_AUX = aux_problem.to_extended_tableau()
    R, V = len(aux_problem.constraints), len(aux_problem.variables)
    
    status = ""
    found = False
    while not found:
        col = find_pivot_column_extended(T_AUX, R, V)
        if col == None:
            found = True
            continue
        row = find_pivot_row_extended(T_AUX, col, R, V)
        if row == None:
            found = True
            status = SYMPLEX_UNBOUNDED
            continue
        T_AUX = pivot_extended(T_AUX, row, col, R, V)
    opt_aux = T_AUX[0,-1]
    
    optimal_value = 0
    if opt_aux < 0:
        status = SYMPLEX_INFEASIBLE
    elif opt_aux == 0:
        slack_model = standard_model.to_slack_form()
        T = slack_model.to_extended_tableau()
        R, V = len(slack_model.constraints), len(slack_model.variables)
        found = False
        while not found:
            col = find_pivot_column_extended(T, R, V)
            if col == None:
                found = True
                continue
            row = find_pivot_row_extended(T, col, R, V)
            if row == None:
                found = True
                status = SYMPLEX_UNBOUNDED
                continue
            T = pivot_extended(T, row, col, R, V)
        optimal_value = T[0,-1]
        status = SYMPLEX_OPTIMAL
        # values = T[0,R+1:-1]
        values = dict()
        for i in range(V):
            values[slack_model.variables[i]] = T[0,R+1+i]
    return status, optimal_value, values

if __name__ == "__main__":
    max_or_min, obj_function, constraints = read_input(sys.argv[1])
    status, optimal_value, values = two_phase_symplex(max_or_min, obj_function, constraints)
    print("Status:", status)
    if status == SYMPLEX_OPTIMAL:
        print("Objetivo:", optimal_value)
        print("Solução:")
        vs = list()
        for i in values:
            if i.name[:1] == "_":
                for j in values:
                    if i != j and j.name[:2] == "__":
                        if i.name[1:] == j.name[2:]:
                            i_value = values[i]
                            j_value = values[j]
                            # vs[sp.Symbol(f"{i.name[1:]}")] = j_value-i_value
                            vs.append((sp.Symbol(f"{i.name[1:]}"),j_value-i_value))
            else: vs.append((sp.Symbol(f"{i.name}"),values[i]))
        
        vs = sorted(vs, key=lambda x : x[0].name)
        for i in vs:
            if i[0].name[0] != "s" and i[0].name[0] != "_":
                print(i[0].name, ':', i[1], end=" ", sep='')
        print()
