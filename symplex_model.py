from symplex_utils import *

class Model:
    def __init__(self) -> None:
        self.optimization_type = SYMPLEX_MAX
        self.objective_function_expr = sp.Expr()
        self.variables = list()
        self.constraints = list()
        self.non_negative_constraints = list()
        self.slack_vars = list()

    def variable(self, symbol: sp.Symbol):
        if not symbol in self.variables:
            self.variables.append(symbol)

    def objective_function(self, max_or_min: bool, function: sp.Expr):
        self.objective_function_expr = function
        self.optimization_type = max_or_min

    def constraint(self, constraint: sp.Expr):
        if len(constraint.free_symbols) == 1 and constraint.rhs == 0:
            self.non_negative_constraints.append(constraint)
        else:
            self.constraints.append(constraint)
            
        for i in constraint.free_symbols:
            self.variable(i)

    def to_standard_form(self):
        standard_model = Model()

        # non-negative constraints correction
        # if variable xi is not positive, substitute by xi_ - xi__
        tmp = self
        for v in self.variables:
            positive = False
            for c in self.non_negative_constraints:
                if c.has(v):
                    positive = True
            if not positive:
                tmp = self.substitute(v)

        # y >= K ? -y <= -K : 0
        for i in range(len(tmp.constraints)):
            new_c = 0
            c = tmp.constraints[i]

            if c.has(sp.core.relational.Ge):
                new_c = -c.lhs <= -c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        for i in range(len(tmp.non_negative_constraints)):
            new_c = 0
            c = tmp.non_negative_constraints[i]

            if c.has(sp.core.relational.Le):
                new_c = - c.lhs >= - c.rhs
            else:
                new_c = c
            standard_model.constraint(new_c)

        # min f(X) ? max -f(X) : 0
        standard_model.optimization_type = SYMPLEX_MAX

        if tmp.optimization_type == SYMPLEX_MIN:
            standard_model.objective_function(
                SYMPLEX_MAX, -tmp.objective_function_expr)

        else:
            standard_model.objective_function(
                SYMPLEX_MAX, tmp.objective_function_expr)

        for v in sorted([i for i in standard_model.objective_function_expr.free_symbols], key=lambda x : x.name):
            standard_model.variable(v)

        return standard_model

    def to_slack_form(self):
        slack_model = Model()
        
        slack_model.objective_function(SYMPLEX_MAX, self.objective_function_expr)
        slack_model.variables = self.variables
        
        constraints = []
        slack_model.non_negative_constraints = self.non_negative_constraints
        for i in range(len(self.constraints)):
            c = self.constraints[i]
            constraints.append(Equation(c.lhs + sp.Symbol(f"s{i+1}"), c.rhs))
            slack_model.variable(sp.Symbol(f"s{i+1}"))
            slack_model.slack_vars.append(sp.Symbol(f"s{i+1}"))
            slack_model.non_negative_constraints.append(sp.parse_expr(f"s{i+1} >= 0"))
        slack_model.constraints = constraints
        
        return slack_model
    
    def to_tableau(self):
        m, n = len(self.constraints), len(self.variables)
        A = np.zeros(shape=[m+1,n+1], dtype=sp.Expr)
        
        A[0,0] = 1
        
        for i in range(1, m+1):
            A[i,0] = 0
        
        coefs = []
        for v in self.variables:
            c = extract_coefficient(self.objective_function_expr, v)
            coefs.append(c)
        for i in range(1, n+1):
            A[0,i] = -coefs[i-1]
        
        A_tmp = [] 
        for c in self.constraints:
            coefs = []
            for v in self.variables:
                coefs.append(extract_coefficient(c.lhs, v))
            A_tmp.append(coefs)
        for i in range(1, m+1):
            for j in range(1, n+1):
                A[i,j] = A_tmp[i-1][j-1]
        
        b = [0]
        for c in self.constraints:
            b.append(c.rhs)
        b = np.array(b, dtype=sp.Expr)
        
        # x = [sp.Symbol("_w")]
        # for v in self.variables:
        #     x.append(v)
        # x = np.array(x, dtype=sp.Expr)
        
        T = np.zeros(shape=[m+1,n+2], dtype=sp.Expr)
        for i in range(0,m+1):
            T[i,-1] = b[i]
            for j in range(0,n+1):
                T[i,j] = A[i,j]
                
        return T
    
    def to_extended_tableau(self) -> np.ndarray:
        R, V = len(self.constraints), len(self.variables)
        L, C = R+1, V+R+1
        tableau = np.zeros(dtype=sp.Expr, shape=[L,C])
        
        # identity matrix
        for i in range(0,L-1):
            tableau[i+1,i] = 1
            
        coefs = []
        for v in self.variables:
            c = extract_coefficient(self.objective_function_expr, v)
            coefs.append(c)
        for i in range(R, R+V):
            tableau[0,i] = -coefs[i-R]
            
        A_tmp = [] 
        for c in self.constraints:
            coefs = []
            for v in self.variables:
                coefs.append(extract_coefficient(c.lhs, v))
            A_tmp.append(coefs)
        for i in range(R):
            for j in range(V):
                tableau[i+1,j+R] = A_tmp[i][j]
        
        b = [0]
        for c in self.constraints:
            b.append(c.rhs)
        for i in range(R+1):
            tableau[i,-1] = b[i]
        
        return tableau
    
    # UTILS
    def generate_aux_problem(self):
        aux_problem = Model()
        
        for i in range(len(self.variables)):
            aux_problem.variable(sp.Symbol(f"x{i+1}"))
            aux_problem.constraint(sp.parse_expr(f"x{i+1}>=0"))
            
        for i in range(len(self.constraints)):
            aux_problem.variable(sp.Symbol(f"u{i+1}"))
            aux_problem.constraint(sp.parse_expr(f"u{i+1}>=0"))
            
        for i in range(len(self.constraints)):
            ui = -1
            if self.constraints[i].rhs >= 0: ui = 1
            lhs = self.constraints[i].lhs + ui*sp.Symbol(f"u{i+1}")
            rhs = self.constraints[i].rhs
            if rhs < 0:
                lhs = -lhs
                rhs = -rhs
            
            aux_problem.constraints.append(Equation(lhs, rhs))
            
        of = 0
        for i in range(len(self.constraints)):
            of -= sp.Symbol(f"u{i+1}")
        aux_problem.objective_function(SYMPLEX_MAX, of)
        
        return aux_problem
    
    def substitute(self, v):
        new = Model()
        
        __v = sp.Symbol(f"__{v.name}")
        _v = sp.Symbol(f"_{v.name}")

        for i in range(len(self.constraints)):
            c = self.constraints[i]
            new.constraint(c.subs(v, _v-__v))

        new_of = self.objective_function_expr.subs(
            v, _v-__v)
        
        new.objective_function(SYMPLEX_MAX, new_of)

        vs = self.variables
        vs.remove(v)
        new.variables = vs
        new.variable(__v)
        new.variable(_v)

        new_non_negative_constraints = self.non_negative_constraints
        for i in range(len(new_non_negative_constraints)):
            c = new_non_negative_constraints[i]
            if c.has(v):
                new_non_negative_constraints.remove(c)
                new.constraint(c.subs(v, _v-__v))
        new_non_negative_constraints.append(_v >= 0)
        new_non_negative_constraints.append(__v >= 0)
        
        new.non_negative_constraints = new_non_negative_constraints
        
        return new
    
    def rename_variable(self, old: sp.Symbol, new: sp.Symbol) -> None:
        # rename in self.variables
        for i in range(len(self.variables)):
            if self.variables[i].name == old.name:
                self.variables[i] = new
                
        # rename in of
        self.objective_function_expr = self.objective_function_expr.subs(old, new)
        
        # rename in constraints
        for i in range(len(self.constraints)):
            if type(self.constraints[i]) != Equation:
                self.constraints[i] = self.constraints[i].subs(old, new)
            else:
                self.constraints[i] = Equation(self.constraints[i].lhs.subs(old, new), self.constraints[i].rhs.subs(old, new))
        
        # rename in non_negative_constraints
        for i in range(len(self.non_negative_constraints)):
            self.non_negative_constraints[i] = self.non_negative_constraints[i].subs(
                old, new)
            
    def reset_variable_names(self):
        for i in range(len(self.variables)):
            self.rename_variable(self.variables[i], sp.Symbol(f"k{i}"))
            
        for i in range(len(self.variables)):
            self.rename_variable(sp.Symbol(f"k{i}"), sp.Symbol(f"x{i+1}"))

    def show(self):
        if self.optimization_type:
            print("MIN")
        elif not (self.optimization_type):
            print("MAX")
        else:
            raise SymplexInvalidExpr

        print("Objective: \t", self.objective_function_expr)
        print("Variables: \t", self.variables)
        print("Constraints: ")
        for i in self.constraints:
            if type(i) != Equation:
                print("\t\t", i)
            else:
                print("\t\t", i.lhs, " == ", i.rhs)
        print("Non-negative Constraints: ")
        for i in self.non_negative_constraints:
            print("\t\t", i)

