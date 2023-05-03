from symplex_constraint import *
from symplex_var_table import *
from typing import Tuple

SYMPLEX_MIN = "MIN"
SYMPLEX_MAX = "MAX"

class Model:
    def __init__(self) -> None:
        self.variables: set = set()
        self.constraints: set = set()
        self.objective: sp.Expr  = sp.Expr()
        self.min_or_max: Union[SYMPLEX_MAX, SYMPLEX_MIN] = SYMPLEX_MAX

    def add_variable(self, 
                 variable: sp.Symbol) -> None:
        
        self.variables.add(variable)

    def add_constraint(self, 
                   constraint: Constraint) -> None:
        
        t = sp.Symbol("t")
        if constraint.has(t):
            constraint = constraint.subs(t, sp.Symbol(f"u{len(self.constraints)+1}"))
            c = Constraint(sp.Symbol(f"u{len(self.constraints)+1}", 0))
            c.non_negativity = True
            self.constraints.append(c)
        
        self.constraints.add(constraint)
        for v in constraint.free_symbols():
            self.add_variable(v)
        
    def set_objective_function(self, 
                           min_or_max: Union[SYMPLEX_MAX, SYMPLEX_MIN], 
                           function: sp.Expr) -> None:
        
        if min_or_max == SYMPLEX_MIN:
            function = - function
        self.objective = function
        for v in function.free_symbols:
            self.add_variable(v)

    def extract_objective_coefficients(self):
        return self.objective.as_coefficients_dict()
    
    def extract_constraints_coefficients(self):
        dicts = []
        for i in self.constraints:
            dicts.append(i.as_coefficients_dict())
        return dicts
    
    def subs(self, old, new) -> None:
        self.variables.remove(old)
        for v in new.free_symbols:
            self.variables.add(v)
        
            c = Constraint(v, 0)
            c.non_negativity = True
            self.constraints.add(c)
            
        for c in self.constraints:
            if c.has(old):
                c.subs(old, new)


    def show(self) -> None:
        print(f"MAX\t{self.objective}")
        print(f"s.t.:")
        for c in self.constraints:
            print(f"\t{c}")
        print(f"vars:\t{[i for i in self.variables]}")

def modelFactory(min_or_max: Union[SYMPLEX_MAX, SYMPLEX_MIN], 
                 objective_function: sp.Expr, 
                 constraints: List[Constraint]) -> Model:
    
    model = Model()
    model.set_objective_function(min_or_max, objective_function)
    for c in constraints:
        model.add_constraint(c)
    return model

def standard_variables(model: Model) -> Tuple[Model, VarTable]:
    var_table = VarTable()
    
    variables = model.variables.copy()
    
    for v in variables:
        non_negativity = False
        
        for c in model.constraints:
            if c.non_negativity and c.has(v):
                non_negativity = True
                
        if not non_negativity:
            _v, __v = sp.Symbol(f"_{v.name}"), sp.Symbol(f"__{v.name}")
            model.subs(v, _v-__v)
            var_table.add(v, _v-__v)
    
    return model, var_table
    

if __name__ == "__main__":
    m = Model()
    m.set_objective_function(SYMPLEX_MIN, sp.parse_expr("x1 + 2*x2 - x3"))
    m.add_constraint(parse_constraint("x1 + x2 <= 3"))
    m.add_constraint(parse_constraint("x1 - x3 == 7"))
    m.add_constraint(parse_constraint("x1 >= 0"))
    m.show()
