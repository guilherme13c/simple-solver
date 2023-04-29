from symplex import *
import sys


def main():
    input_file_name = str(sys.argv[1])

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

    model = Model()

    variables = obj_function.free_symbols
    for v in variables:
        model.variable(v)

    model.objective_function(max_or_min, obj_function)

    for c in constraints:
        model.constraint(c)


    sp.init_printing(use_unicode=True, use_latex=True)
    
    print("input model: \n")
    model.show()
    print("-------------------------------------")

    standard_model = model.to_standard_form()
    standard_model.reset_variable_names()

    print("standard model: \n")
    standard_model.show()
    print("-------------------------------------")

    slack_model = standard_model.to_slack_form()
    # slack_model.reset_variable_names()
    
    print("slack model: ")
    slack_model.show()
    print("-------------------------------------")
    
    T = slack_model.to_tableau()
    print("tableau: ")
    sp.pprint(sp.Matrix(T))

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
        print("############################")
        T = pivot(T, row, col)
        sp.pprint(sp.Matrix(T))
    
    print("-------------------------------------")
    sp.pprint(sp.Matrix(T))

if __name__ == "__main__":
    main()
