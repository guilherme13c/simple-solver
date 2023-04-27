from simplex import *
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
        "".join(obj_function))
    constraints = [Model.generate_symbolic_expr(
        "".join(i)) for i in constraints]
    
    model = Model()
    
    variables = obj_function.free_symbols
    for v in variables:
        model.variable(v)
        
    model.objective_function(max_or_min, obj_function)
    
    for c in constraints:
        model.constraint(c)
        
    model.show()


if __name__ == "__main__":
    main()
