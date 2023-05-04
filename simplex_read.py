def read_input(file):
    file = open(file, "r")
    
    lines = file.readlines()
    
    optimization = lines[0].strip().split(" ")[0]
    objective_function = "".join(lines[0].strip().split(" ")[1:])
    constraints = []
    
    for l in lines[1:]:
        constraints.append(l.strip())
        
    return optimization, objective_function, constraints

class OutputManager:
    def __init__(self, file):
        self.file = open(file, "w")
    
    def print_to_file(self, expr="", end='\n'):
        self.file.write(f"{expr}"+end)


if __name__ == "__main__":
    import sys
    optimization, objective_function, constraints = read_input(sys.argv[1])
