from typing import Any

class VarTable:
    def __init__(self):
        self.table = dict()

    def add(self, key, value):
        self.table[key] = value
        
    def __getitem__(self, key) -> Any:
        return self.table[key]

    def __contains__(self, key) -> bool:
        return key in self.table.keys()