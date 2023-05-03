from symplex_constraint import *
from symplex_error import *
from symplex_model import *
import numpy as np


class Tableau:
    def __init__(self, model: Model):
        self.model = model
        self.variables = sorted(list(model.variables), key=lambda x: x.name)

        self.m = len([i for i in model.constraints if not i.non_negativity])+1
        self.n = len(model.variables)+self.m

        self.table = np.zeros(shape=[self.m, self.n], dtype=sp.AtomicExpr)

        # fills identity part
        for i in range(self.m-1):
            self.table[i+1, i] = 1

        # fills first row
        objective_coefficients = self.model.extract_objective_coefficients()
        for i in range(len(self.variables)):
            if self.variables[i] in objective_coefficients.keys():
                self.table[0,self.m-1+i] = -objective_coefficients[self.variables[i]]

        # fill constraints matrix
        # constraint_coefficients = self.model.extract_constraints_coefficients()
        # for i in range(len(constraint_coefficients)):
        #     for j in range(len(self.variables)):
        #         if self.variables[j] in constraint_coefficients[i].keys():
        #             self.table[i+1,self.m-1+i] = constraint_coefficients[i][self.variables[j]]

    def show(self):
        sp.pprint(sp.Matrix(self.table))
        print("Vars:\t", self.variables)
