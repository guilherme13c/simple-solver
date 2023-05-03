# from symplex_utils import generate_symbolic_expr

# def read_input(input_file_name):
#     input_data = []
#     input_file = open(input_file_name, "r")
#     for l in input_file:
#         input_data.append(l.split(" "))

#     max_or_min = (input_data[0][0] == "MIN")
#     obj_function = input_data[0][1:]
#     constraints = input_data[1:]

#     obj_function = generate_symbolic_expr(
#         " ".join(obj_function))

#     aux = []
#     for i in constraints:
#         c = generate_symbolic_expr(" ".join(i))
#         if type(c) == list:
#             aux.append(c[0])
#             aux.append(c[1])
#         else:
#             aux.append(c)
#     constraints = aux

#     return max_or_min, obj_function, constraints

from symplex_tableau import *
from symplex_var_table import *


def read_input(input_file_name):
    input_data = []
    input_file = open(input_file_name, "r")
    for l in input_file:
        input_data.append(l.split(" "))

    max_or_min = input_data[0][0]
    obj_function = input_data[0][1:]
    constraints = input_data[1:]

    obj_function = sp.parse_expr(
        " ".join(obj_function))

    constraints = parse_constraints(constraints)

    for i in range(len(constraints)):
        constraints[i] = constraints[i].subs(
            sp.Symbol("t"), sp.Symbol(f"u{i+1}"))

    return max_or_min, obj_function, constraints
