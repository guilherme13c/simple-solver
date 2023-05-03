from symplex_constraint import *
from symplex_error import *
from symplex_model import *
import numpy as np

class Tableau:
    def __init__(self, model: Model):
        self.model = model
        
        self.m = len(model.constraints)+1
        self.n = len(model.variables)+len(model.constraints)+1
        
        self.table = np.zeros(shape=[self.m,self.n], dtype=sp.AtomicExpr)
        
        for i in range(1, self.m):
            for j in range(0, self.m):
                self.table[i,j] = 1
        
        objective_coefficients = self.model.extract_objective_coefficients()
        for i in range(len(self.model.variables)):
            self.table[0,self.m-1+i] = objective_coefficients[i]
        
    def show(self):
        sp.pprint(sp.Matrix(self.table))