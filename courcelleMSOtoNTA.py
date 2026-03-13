from courcelleAutomataConstruction import *
from treeAutomata import *
import re
from StringCase.utils import gen_courcelle_alphabet

class courcelle_MSO_to_NTA_Parser:
    def __init__(self, alphabet, twd, k):
        self.alphabet = alphabet
        self.base_alphabet = gen_courcelle_alphabet(treewidth=twd, k=k)
        self.k = k
        self.twd = twd
        self.variable_counter = 1
        self.bound_variables = {}
        self.variable_types = {}

    def _split_at_comma(self, s):
        depth = 0
        for i, char in enumerate(s):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                return s[:i].strip(), s[i+1:].strip()
        raise ValueError(f"Could not find comma to split: {s}")
    
    def build_ast(self, formula):
        formula = formula.strip()
        if formula.startswith('∃'):
            fo_match = re.match(r'∃([a-z_]\w*)\((.*)\)', formula)
            so_match = re.match(r'∃([A-Z_]\w*)\((.*)\)', formula)
            quant_match = fo_match or so_match
            if quant_match:
                var_name = quant_match.group(1).strip()
                print(f"Processing quantifier for variable: {var_name}")
                subformula = quant_match.group(2).strip()
                var_type = 'first' if fo_match else 'second'
                ast_type = 'exists_first' if fo_match else 'exists_second'
                self.bound_variables[var_name] = self.variable_counter
                self.variable_types[var_name] = var_type
                self.variable_counter += 1
                return {
                    'type': ast_type,
                    'var': var_name,
                    'var_type': var_type,
                    'subformula': self.build_ast(subformula)
                }
        # in the case of universal quantifier we replace it with negated existential (∀x:f -> ¬∃x:¬f)
        elif formula.startswith('∀'):
            fo_match = re.match(r'∀([a-z_]\w*)\((.*)\)', formula)
            so_match = re.match(r'∀([A-Z_]\w*)\((.*)\)', formula)
            quant_match = fo_match or so_match
            if quant_match:
                var_name = quant_match.group(1).strip()
                subformula = quant_match.group(2).strip()
                var_type = 'first' if fo_match else 'second'
                exists_type = 'exists_first' if fo_match else 'exists_second'
                self.bound_variables[var_name] = self.variable_counter
                self.variable_types[var_name] = var_type
                self.variable_counter += 1
                if var_type == "first":
                    return {
                    'type': 'not',
                    'subformula': {
                        'type': "forall_first",
                        'var': var_name,
                        'var_type': var_type,
                        'subformula': {'type' : 'not', 'subformula': self.build_ast(subformula)}
                        }
                    }
                    
                if var_type == "second":    
                    return {
                    'type': 'not',
                    'subformula': {
                        'type': exists_type,
                        'var': var_name,
                        'var_type': var_type,
                        'subformula': {'type' : 'not', 'subformula': self.build_ast(subformula)}
                        }
                    }

        # Boolean connectives
        elif formula.startswith('not'):
            if formula.startswith('not(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
            else:
                inner = formula[3:].strip()
            return {
                'type': 'not',
                'subformula': self.build_ast(inner)
            }
        elif formula.startswith('and'):
            if formula.startswith('and(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'and',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('or'):
            if formula.startswith('or(') and formula.endswith(')'):
                inner = formula[3:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'or',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('->'):
            if formula.startswith('->(') and formula.endswith(')'):
                inner = formula[3:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'implies',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('<->'):
            if formula.startswith('<->(') and formula.endswith(')'):
                inner = formula[4:-1]  # Remove '<->(' and ')'
                left, right = self._split_at_comma(inner)
                #print(f"<-> with left: {left}, right: {right}")
                # A <-> B is equivalent to (A -> B) and (B -> A)
                return {
                    'type': 'and',
                    'left': {
                        'type': 'implies',
                        'left': self.build_ast(left),
                        'right': self.build_ast(right)
                    },
                    'right': {
                        'type': 'implies',
                        'left': self.build_ast(right),
                        'right': self.build_ast(left)
                    }
                }
        # Set operations
        elif formula.startswith('in1(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
                set_var, elem_var = self._split_at_comma(inner)
                return {
                    'type': 'in1',
                    'set_var': set_var,
                    'elem_var': elem_var
                }
        elif formula.startswith('in2(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
                set_var, elem_var = self._split_at_comma(inner)
                return {
                    'type': 'in2',
                    'set_var': set_var,
                    'elem_var': elem_var
                }
        elif formula.startswith('subset(') and formula.endswith(')'):
                inner = formula[7:-1].strip()
                set1_var, set2_var = self._split_at_comma(inner)
                return {
                    'type': 'subset',
                    'set1_var': set1_var,
                    'set2_var': set2_var
                }
        # Graph predicates
        elif formula.startswith('vertices(') and formula.endswith(')'):
                inner = formula[9:-1].strip()
                set_var = self._split_at_comma(inner)
                return {
                    'type': 'vertices',
                    'set_var': set_var
                }
        elif formula.startswith('edges(') and formula.endswith(')'):
                inner = formula[6:-1].strip()
                set_var = self._split_at_comma(inner)
                return {
                    'type': 'edges',
                    'set_var': set_var
                }
        raise ValueError(f"Unrecognized formula: {formula}")
    
    def build_automaton(self, ast):
        print(f"Building automaton for AST node: {ast}")
        if ast['type'] in ('exists', 'exists_first'):
            var = ast['var']
            var_idx = self.bound_variables[var]
            sub_automaton = self.build_automaton(ast['subformula'])

            singleton = singl(var_idx, self.alphabet, self.twd, self.k)

            combined = singleton.cut(sub_automaton)

            automaton = combined.project_courcelle(self.alphabet, self.twd, var_idx, verbose=False)

            self.k = self.k - 1
            return automaton
        
        elif ast['type'] == 'exists_second':
            var = ast['var']
            var_idx = self.bound_variables[var]
            sub_automaton = self.build_automaton(ast['subformula'])
            print("Sub Automaton:", sub_automaton.input_symbols)
            automaton = sub_automaton.project_courcelle(self.alphabet, self.twd, var_idx, verbose=False)
            self.k = self.k - 1
            return automaton
        
        elif ast['type'] == 'forall_first':
            var = ast['var']
            var_idx = self.bound_variables[var]
            sub_automaton = self.build_automaton(ast['subformula'])

            singleton = singl(var_idx, self.alphabet, self.twd, self.k)
            combined = singleton.complement().union(sub_automaton)

            automaton = combined.project_courcelle(self.alphabet, self.twd, var_idx, verbose=False)
            self.k = self.k - 1
            return automaton


        elif ast['type'] == 'not':
            sub_automaton = self.build_automaton(ast['subformula'])
            #print(sub_automaton.input_symbols)
            return sub_automaton.complement()
        
        elif ast['type'] == 'and':
            left_automaton = self.build_automaton(ast['left'])
            right_automaton = self.build_automaton(ast['right'])
            return left_automaton.cut(right_automaton)
        
        elif ast['type'] == 'or':
            left_automaton = self.build_automaton(ast['left'])
            right_automaton = self.build_automaton(ast['right'])
            return left_automaton.union(right_automaton)
        
        elif ast['type'] == 'implies':
            left_automaton = self.build_automaton(ast['left'])
            right_automaton = self.build_automaton(ast['right'])
            left_complement = left_automaton.complement()
            return left_complement.union(right_automaton)

        elif ast['type'] == 'in1':
            set_var = ast['set_var']
            elem_var = ast['elem_var']
            set_idx = self.bound_variables[set_var]
            elem_idx = self.bound_variables[elem_var]
            return in1(set_idx, elem_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'in2':
            set_var = ast['set_var']
            elem_var = ast['elem_var']
            set_idx = self.bound_variables[set_var]
            elem_idx = self.bound_variables[elem_var]
            return in2(set_idx, elem_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'subset':
            set1_var = ast['set1_var']
            set2_var = ast['set2_var']
            set1_idx = self.bound_variables[set1_var]
            set2_idx = self.bound_variables[set2_var]
            return subset(set1_idx, set2_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'vertices':
            set_var = ast['set_var']
            set_idx = self.bound_variables[set_var]
            return vertices(set_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'edges':
            set_var = ast['set_var']
            set_idx = self.bound_variables[set_var]
            return edges(set_idx, self.alphabet, self.twd, self.k)
        

if __name__ == "__main__":
   
    treewidth = 2
    k = 4
    alphabet = gen_courcelle_alphabet(treewidth, 0)

    print(alphabet)
    print("------------------------------")


    a1 = Node("ab", 1, [])
    a2 = Node("ba", 2, [])
    a3 = Node("bc", 3, [])
    a4 = Node("cb", 4, [])
    a5 = Node("ac", 5, [])
    a6 = Node("ca", 6, [])
    a7 = Node("//", 7, [a1, a2])
    a8 = Node("//", 8, [a3, a4])
    a9 = Node("//", 9, [a5, a6])
    a10 = Node("//", 10, [a8, a9])
    a11 = Node("//", 11, [a7, a10])
    a12 = Node("miv_c", 12, [a11])
    a13 = Node("miv_b", 13, [a12])
    a14 = Node("miv_a", 14, [a13])

    #Quad Graph in F^HR given the belongings to the sets 
    b1 = Node("ab", 1, [])
    b2 = Node("ba", 2, [])
    b3 = Node("bc", 3, [])
    b4 = Node("cb", 4, [])
    b5 = Node("ab", 5, [])
    b6 = Node("ba", 6, [])
    b7 = Node("bc", 7, [])
    b8 = Node("cb", 8, [])
    b9 = Node("//", 9, [b1, b2])
    b10 = Node("//", 10, [b3, b4])
    b11 = Node("//", 11, [b5, b6])
    b12 = Node("//", 12, [b7, b8])
    b13 = Node("//", 13, [b9, b10])
    b14 = Node("//", 14, [b11, b12])
    b15 = Node("miv_b", 15, [b13])
    b16 = Node("miv_b", 16, [b14])
    b17 = Node("//", 17, [b15, b16])
    b18 = Node("miv_c", 17, [b17])
    b19 = Node("miv_a", 18, [b18])

    tree_triangle = RootedTree(a14, [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14])
    tree_quad = RootedTree(b19, [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17, b18, b19])

    parser = courcelle_MSO_to_NTA_Parser(alphabet, treewidth, k)
    #formula = "∃X1(∃X2(∃X3(and(in1(X3, X1),in2(X3, X2)))))"

    formula = "∃X(∃Y(∀u(∀v(->(and(in1(Y, u),in2(Y, v) ),not(or(and(subset(u,X),subset(v,X)),and(not(subset(u,X)),not(subset(v,X))))))))))"

    #formula = "∃a(∃b(∃c(∃X(∃Y(∃Z(and(   and(in1(X, a), in2(X, b) ),  " \
    #"                                and(and(in1(Y, a), in2(Y, c))," \
    #"                                    and(in1(Z, b), in2(Z, c))))))))))"

    ast = parser.build_ast(formula)

    automaton = parser.build_automaton(ast)

    #print("automaton transitions: ", automaton.transitions)

    print(automaton.input_symbols)

    print("Quad Graph, triangle exsists:", automaton.nta_run(tree_quad))
    print("Triangle Graph, traiangle exists:", automaton.nta_run(tree_triangle))