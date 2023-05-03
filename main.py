from read_input import *
import sys
from symplex_tableau import *


def main():
    max_or_min, obj_function, constraints = read_input(sys.argv[1])

    model = modelFactory(max_or_min, obj_function, constraints)
    model.show()

    model, var_table = standard_variables(model)

    model.show()
    print(var_table.table)


if __name__ == "__main__":
    main()

# TODO: fix additional variable insertion
# adding variables isn't adding a respective non negativity constraint
