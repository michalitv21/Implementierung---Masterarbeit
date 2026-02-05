from treeAutomataConstruction import singl, left, right, sub, symb
from treeAutomata import *
import re

class MSO_to_NTA_Parser:
    def __init__(self, alphabet, k):
        self.alphabet = alphabet
        self.k = k
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
                return {
                    'type': 'not',
                    'subformula': {
                        'type': exists_type,
                        'var': var_name,
                        'var_type': var_type,
                        'subformula': {'type' : 'not', 'subformula': self.build_ast(subformula)}
                        }
                    }
        elif formula.startswith('left'):
            # Use parentheses-aware splitting
            if formula.startswith('left(') and formula.endswith(')'):
                inner = formula[5:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'left',
                    'left': left,
                    'right': right
                }
        elif formula.startswith('right'):
            # Use parentheses-aware splitting
            if formula.startswith('right(') and formula.endswith(')'):
                inner = formula[6:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'right',
                    'left': left,
                    'right': right
                }
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
        elif formula.startswith('in'):
            if formula.startswith('in(') and formula.endswith(')'):
                inner = formula[3:-1].strip()
                set_var, elem_var = self._split_at_comma(inner)
                return {
                    'type': 'in',
                    'set_var': set_var,
                    'elem_var': elem_var
                }
        elif formula.startswith('P_'):
            pred_match = re.match(r'P_([a-zA-Z_]\w*)\((.*)\)', formula)
            if pred_match:
                symbol = pred_match.group(1).strip()
                var = pred_match.group(2).strip()
                return {
                    'type': 'predicate',
                    'symbol': symbol,
                    'var': var
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
        raise ValueError(f"Unrecognized formula: {formula}")
    
    def build_automaton(self, ast):
        if ast['type'] in ('exists', 'exists_first'):
            var = ast['var']
            var_idx = self.bound_variables[var]
            sub_automaton = self.build_automaton(ast['subformula'])

            singleton = singl(var_idx, self.alphabet, self.k)

            combined = singleton.cut(sub_automaton)

            automaton = combined.project(self.alphabet, var_idx)

            self.k = self.k - 1
            return automaton
        
        elif ast['type'] == 'exists_second':
            var = ast['var']
            var_idx = self.bound_variables[var]
            sub_automaton = self.build_automaton(ast['subformula'])
            automaton = sub_automaton.project(self.alphabet, var_idx)
            self.k = self.k - 1
            return automaton
        
        elif ast['type'] == 'not':
            sub_automaton = self.build_automaton(ast['subformula'])
            print(sub_automaton.input_symbols)
            return sub_automaton.complement()
        
        elif ast['type'] == 'left':
            left_var = ast['left']
            right_var = ast['right']
            left_idx = self.bound_variables[left_var]
            right_idx = self.bound_variables[right_var]
            return left(left_idx, right_idx, self.alphabet, self.k)
        
        elif ast['type'] == 'right':
            left_var = ast['left']
            right_var = ast['right']
            left_idx = self.bound_variables[left_var]
            right_idx = self.bound_variables[right_var]
            return right(left_idx, right_idx, self.alphabet, self.k)
        
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
        
        elif ast['type'] == 'in':
            print("IN not implemented yet!")
            print("TODO: Implement IN operator construction!")
            pass

        elif ast['type'] == 'predicate':
            char = ast['symbol']
            var = ast['var']
            var_idx = self.bound_variables[var]
            return symb(char, var_idx, self.alphabet, self.k)
        
if __name__ == "__main__":
    alphabet = {
        "a":2,
        "b":2,
        "c":2,
        "x":0,
        "y":0
    }

    t1n1 = Node("x", 1, [])
    t1n2 = Node("x", 2, [])
    t1n3 = Node("y", 3, [])
    t1n4 = Node("y", 4, [])
    t1n5 = Node("x", 5, [])
    t1n6 = Node("y", 6, [])
    t1n7 = Node("x", 7, [])
    t1n8 = Node("y", 8, [])
    t1n9 = Node("c", 9, [t1n1, t1n2])
    t1n10 = Node("a", 10, [t1n3, t1n4])
    t1n11 = Node("a", 11, [t1n5, t1n6])
    t1n12 = Node("c", 12, [t1n7, t1n8])
    t1n13 = Node("b", 13, [t1n9, t1n10])
    t1n14 = Node("b", 14, [t1n11, t1n12])
    t1n15 = Node("a", 15, [t1n13, t1n14])

    t2n1 = Node("x", 1, [])
    t2n2 = Node("x", 2, [])
    t2n3 = Node("y", 3, [])
    t2n4 = Node("y", 4, [])
    t2n5 = Node("x", 5, [])
    t2n6 = Node("y", 6, [])
    t2n7 = Node("x", 7, [])
    t2n8 = Node("y", 8, [])
    t2n9 = Node("a", 9, [t2n1, t2n2])
    t2n10 = Node("a", 10, [t2n3, t2n4])
    t2n11 = Node("a", 11, [t2n5, t2n6])
    t2n12 = Node("c", 12, [t2n7, t2n8])
    t2n13 = Node("b", 13, [t2n9, t2n10])
    t2n14 = Node("b", 14, [t2n11, t2n12])
    t2n15 = Node("a", 15, [t2n13, t2n14])

    tree1 = RootedTree(t1n15, [t1n1, t1n2, t1n3, t1n4, t1n5, t1n6, t1n7, t1n8, t1n9, t1n10, t1n11, t1n12, t1n13, t1n14, t1n15])

    tree2 = RootedTree(t2n15, [t2n1, t2n2, t2n3, t2n4, t2n5, t2n6, t2n7, t2n8, t2n9, t2n10, t2n11, t2n12, t2n13, t2n14, t2n15])

    k = 2

    parser = MSO_to_NTA_Parser(alphabet, k)

    #formula = "∃x(∃y(and(P_a(x),and(P_b(y),left(x,y)))))"
    formula = "∀x(∃y(->(P_b(x),and(P_a(y),left(x,y)))))"
    #formula = "∃x(∃y(and(and(P_b(x),P_c(y)),left(y,x))))"
    
    ast = parser.build_ast(formula)

    automaton = parser.build_automaton(ast)


    print("Tree 1 accepted: ", automaton.nta_run(tree1))
    print("Tree 2 accepted: ", automaton.nta_run(tree2))
