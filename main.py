from symplex import *
import sys

def read_input(input_file_name):
    input_data = []
    input_file = open(input_file_name, "r")
    for l in input_file:
        input_data.append(l.split(" "))

    max_or_min = (input_data[0][0] == "MIN")
    obj_function = input_data[0][1:]
    constraints = input_data[1:]

    obj_function = Model.generate_symbolic_expr(
        " ".join(obj_function))

    aux = []
    for i in constraints:
        c = Model.generate_symbolic_expr(" ".join(i))
        if type(c) == list:
            aux.append(c[0])
            aux.append(c[1])
        else:
            aux.append(c)
    constraints = aux
    
    return max_or_min, obj_function, constraints

def symplex(max_or_min, obj_function, constraints):
    model = Model()

    variables = obj_function.free_symbols
    for v in variables:
        model.variable(v)

    model.objective_function(max_or_min, obj_function)

    for c in constraints:
        model.constraint(c)


    sp.init_printing(use_unicode=True, use_latex=True)
    
    # print("input model: \n")
    # model.show()
    # print("-------------------------------------")

    standard_model = model.to_standard_form()
    standard_model.reset_variable_names()

    # print("standard model: \n")
    # standard_model.show()
    # print("-------------------------------------")

    slack_model = standard_model.to_slack_form()
    # slack_model.reset_variable_names()
    
    # print("slack model: ")
    # slack_model.show()
    # print("-------------------------------------")
    
    T = slack_model.to_tableau()
    # print("tableau: ")
    # sp.pprint(sp.Matrix(T))

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
        # print("############################")
        T = pivot(T, row, col)
        # sp.pprint(sp.Matrix(T))
    
    # print("-------------------------------------")
    # sp.pprint(sp.Matrix(T))

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
    # standard_model.reset_variable_names()
    standard_model.show()
    print("----------------------------------------------------------")
    
    # slack_model = standard_model.to_slack_form()
    # slack_model.reset_variable_names()
    # slack_model.show()
    # print("----------------------------------------------------------")
    
    aux_problem = standard_model.generate_aux_problem()
    
    aux_problem.show()
    print("----------------------------------------------------------")
    
    AUX = aux_problem.to_tableau()
    
    T_AUX = aux_problem.to_extended_tableau()
    sp.pprint(sp.Matrix(T_AUX))
    
    # found = False
    # while not found:
    #     col = find_pivot_column(AUX)
    #     if col == None:
    #         found = True
    #         continue
    #     row = find_pivot_row(AUX, col)
    #     if row == None:
    #         found = True
    #         continue
    #     AUX = pivot(AUX, row, col)
    # opt_aux = AUX[0,-1]
    
    # if opt_aux < 0: return SYMPLEX_INFEASIBLE
    
    # TODO: solve auxiliary problem

if __name__ == "__main__":
    max_or_min, obj_function, constraints = read_input(sys.argv[1])
    # symplex(max_or_min, obj_function, constraints)
    two_phase_symplex(max_or_min, obj_function, constraints)
