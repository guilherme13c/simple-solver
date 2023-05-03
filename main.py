from read_input import *
import sys
from symplex_tableau import *


def main():
    max_or_min, obj_function, constraints = read_input(sys.argv[1])

    model = modelFactory(max_or_min, obj_function, constraints)
    model.show()
    print("----------------------------------------------")

    model, var_table = standard_variables(model)

    model.show()
    print("var table:\t", var_table.table)
    print("----------------------------------------------")

    tableau = Tableau(model)
    tableau.show()

if __name__ == "__main__":
    main()

