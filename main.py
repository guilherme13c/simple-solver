from simplex_read import *
from simplex_parse import *
from simplex_tableau import *
from simplex import *
import sys

def main():
    in_file = sys.argv[1]

    output = OutputManager("output.txt")

    optimization, objective_function, constraints = read_input(in_file)

    optimization, objective_function = parse_objective_function(
        optimization, objective_function)

    for i in range(len(constraints)):
        constraints[i] = ensure_rhs_positivity(constraints[i])

    original_variables = set()
    try: tmp = extract_variables(objective_function)
    except: return 1
    
    original_variables = original_variables.union(tmp)
    for i in range(len(constraints)):
        try: tmp = extract_variables(constraints[i]) 
        except: return 1
        
        original_variables = original_variables.union(tmp)

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
            objective_function = objective_function.replace(
                f'{original_variables[i]}', subs_table[f'{original_variables[i]}'])
            for j in range(len(constraints)):
                constraints[j] = constraints[j].replace(
                    f'{original_variables[i]}', subs_table[f'{original_variables[i]}'])
            constraints.append(f'_{original_variables[i]} >= 0')
            constraints.append(f'__{original_variables[i]} >= 0')

            variables_after_substitution.append(f'__{original_variables[i]}')
            variables_after_substitution.append(f'_{original_variables[i]}')
        else:
            variables_after_substitution.append(original_variables[i])

    slack_variables, constraints = add_slack_variables(constraints)
    additional_variables, constraints = add_additional_variables(constraints)

    for i in additional_variables:
        constraints.append(i+" >= 0")
    for i in slack_variables:
        constraints.append(i+" >= 0")

    if (len(sp.parse_expr(objective_function).free_symbols) == 0): return 1
    tableau = to_tableau(objective_function, constraints,
                         variables_after_substitution, slack_variables, additional_variables)

    tableau = normalize_tableau(tableau)

    auxiliar_objective_function, auxiliar_constraints, auxiliar_variables_after_substitution, auxiliar_slack_variables, auxiliar_additional_variables = generate_auxiliar_problem(
        objective_function, constraints, variables_after_substitution, slack_variables, additional_variables)

    auxiliar_tableau = to_tableau(auxiliar_objective_function, auxiliar_constraints,
                                  auxiliar_variables_after_substitution, auxiliar_slack_variables, auxiliar_additional_variables)

    auxiliar_tableau = normalize_tableau(auxiliar_tableau)

    auxiliar_status, auxiliar_tableau, aux_certificate = simplex(
        auxiliar_tableau)

    if auxiliar_tableau[0, -1] != 0:
        output.print_to_file(f"Status: inviavel")
        output.print_to_file(f"Certificado:")
        for i in aux_certificate:
            output.print_to_file(i, end=' ')
        output.print_to_file()

    else:
        for i in additional_variables:
            tableau = np.delete(tableau, -2, 1)

        status, tableau, certificate = simplex(tableau)

        if status == "unbounded":
            output.print_to_file(f"Status: ilimitado")
            output.print_to_file("Certificado:")
            for i in certificate:
                output.print_to_file(i, end=' ')
            output.print_to_file()

        elif status == "optimal":
            output.print_to_file(f"Status: otimo")
            output.print_to_file(f"Objetivo: {tableau[0,-1]}")
            output.print_to_file("Certificado:")
            for i in certificate:
                output.print_to_file(i, end=' ')
            output.print_to_file()

            output.print_to_file("Solucao: ")

            values = []
            variable_values = dict()
            
            for i in range(len(variables_after_substitution)):
                idx = variables_after_substitution[i]
                variable_values[idx] = tableau[0, i]

            for i in range(len(original_variables)):
                if original_variables[i] in variable_values.keys():
                    values.append(variable_values[original_variables[i]])

                else:
                    substitution = sp.parse_expr(
                        subs_table[original_variables[i]])
                    for j in substitution.free_symbols:
                        substitution = substitution.subs(
                            j.name, variable_values[j.name])
                    values.append(substitution)

            for i in values:
                output.print_to_file(i, end=' ')
            output.print_to_file()


if __name__ == "__main__":
    main()
