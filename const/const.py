import re

class Variable():
    def __init__(self):
        self.path = ""
        self.name = ""
        self.addr = ""
        self.word = ""
        self.bit = ""
        self.n_start = ""
        self.n_end = ""
        self.one_bit = ""
        self.failed = True

class VarGroup():
    "klasa na grupę deklaracji"
    def __init__(self,path):
        self.path = path
        self.variables = []

# pierwsza czesc sciezki do zmiennej w conn
folder = "io_frw_i"

# regexp który znajduje conn file
conn_file_name = re.compile('.*conn_file:\s(\w+\.\w+)')

# regexp który znajduje sciezki do zmiennych dla kazdej grupy
var_path_section = re.compile('('+ folder +'[\w|_|.|/]+)+')

# regex ktory znajduje nazwe zmiennej końcówke sciezki do niej
var_parse = re.compile("(?:(?:\[[0-9|:]*\])*\s*)?(\w+);\s*\/\/\s*(([\w|\.|/]+))[\[|\]]*")               #'bit\s\[([0-9]+):([0-9]+)\]\s([\w|_]+);\s//\s')

# regex poczatku linijki w pliku conn
conn_line_start = '([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s[^\n]*' 

# regex konca linijki w pliku conn
conn_line_end = '(\[([0-9]+)\])*'
# urzycie dwóch powyższych
# conn_line_start + total_path + conn_line_end



# separator
separator = "\n ################################################ \n"

#generates a separated space for function
def createVarFunction(inside, varName) :
    s = ""
    s += "# function for variable " + varName + "\n"
    s += "\n" + inside + "\n"
    s += "# end_of_function for variable " + varName + "\n"
    return s
