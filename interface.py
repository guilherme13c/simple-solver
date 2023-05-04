from simplex_read import *
from simplex_parse import *
from simplex_tableau import *
from simplex import *
import sys

def main():
    in_file = sys.argv[1]
    
    optimization, objective_function, constraints = read_input(in_file)

    optimization, objective_function = parse_objective_function(optimization, objective_function)

    for i in range(len(constraints)):
        constraints[i] = ensure_rhs_positivity(constraints[i])
    
    original_variables = set()
    original_variables = original_variables.union(extract_variables(objective_function))
    for i in range(len(constraints)):
        original_variables = original_variables.union(extract_variables(constraints[i]))
        
    original_variables = sorted(list([v.name for v in original_variables]))
    
    subs_table = dict()
    
    has_non_negativity_constraint = []
    for i in original_variables:
        has = False
        for j in constraints:
            if is_non_negativity_constraint_for(j, i): 
                has = True
                
        has_non_negativity_constraint.append(has)
    
    variables_after_substitution = []
    for i in range(len(original_variables)):
        if not has_non_negativity_constraint[i]:
            subs_table[f'{original_variables[i]}'] = f'(_{original_variables[i]} - __{original_variables[i]})'
            objective_function = objective_function.replace(f'{original_variables[i]}', subs_table[f'{original_variables[i]}'])
            for j in range(len(constraints)):
                constraints[j] = constraints[j].replace(f'{original_variables[i]}', subs_table[f'{original_variables[i]}'])
            constraints.append(f'_{original_variables[i]} >= 0')
            constraints.append(f'__{original_variables[i]} >= 0')
            
            variables_after_substitution.append(f'__{original_variables[i]}')
            variables_after_substitution.append(f'_{original_variables[i]}')
        else:
            variables_after_substitution.append(original_variables[i])
    
    # additional_variables, slack_variables, constraints = add_slack_and_additional_variables(constraints)
    slack_variables, constraints = add_slack_variables(constraints)
    additional_variables, constraints = add_additional_variables(constraints)
    
    for i in additional_variables:
        constraints.append(i+" >= 0")
    for i in slack_variables:
        constraints.append(i+" >= 0")
    
    print(optimization, objective_function)
    [print(i) for i in constraints]
    print(original_variables)
    print(variables_after_substitution)
    print(slack_variables)
    print(additional_variables)

    tableau = to_tableau(objective_function, constraints, variables_after_substitution, slack_variables, additional_variables)
    
    tableau = normalize_tableau(tableau)
    tableau, status, certificate = simplex(tableau)

    sp.pprint(sp.Matrix(tableau))
    print(status)
    print(certificate)
    
    auxiliar_objective_function, auxiliar_constraints, auxiliar_variables_after_substitution, auxiliar_slack_variables, auxiliar_additional_variables = generate_auxiliar_problem(objective_function, constraints, variables_after_substitution, slack_variables, additional_variables)
    
    auxiliar_tableau = to_tableau(auxiliar_objective_function, auxiliar_constraints, auxiliar_variables_after_substitution, auxiliar_slack_variables, auxiliar_additional_variables)
    
    auxiliar_tableau = normalize_tableau(auxiliar_tableau)
    auxiliar_tableau, auxiliar_status, aux_certificate = simplex(auxiliar_tableau)
    
    sp.pprint(sp.Matrix(auxiliar_tableau))
    print(auxiliar_status)
    print(aux_certificate)

if __name__ == "__main__":
    main()
