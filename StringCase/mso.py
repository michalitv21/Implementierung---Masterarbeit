import re
from conversion import singl, le, symb, sub, Automaton
from stringAutomata import Automaton as StringAutomaton

class MSO_Parser:

    def __init__(self, alphabet, k):
        self.alphabet = alphabet
        self.k = k
        self.variable_counter = 1
        self.bound_variables = {}

    def _split_at_comma(self, s):
        """
        Split a string at the first comma that is not inside parentheses.
        Returns a tuple (left, right).
        """
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
        """
        Build an abstract syntax tree (AST) from the formula string.
        This is a simplified parser for demonstration purposes.
        """
        formula = formula.strip()
        if formula.startswith('∃'):
            match = re.match(r'∃([a-zA-Z_]\w*)\((.*)\)', formula)
            if match:
                var_name = match.group(1).strip()
                subformula = match.group(2).strip()
                self.bound_variables[var_name] = self.variable_counter
                self.variable_counter += 1
                return {
                    'type': 'exists',
                    'var': var_name,
                    'subformula': self.build_ast(subformula)
                }
        # in the case of universal quantification we replace it with negated existential (∀x:f -> ¬∃x:¬f)
        elif formula.startswith('∀'):
            match = re.match(r'∀([a-zA-Z_]\w*)\((.*)\)', formula)
            if match:
                var_name = match.group(1).strip()
                subformula = match.group(2).strip()
                self.bound_variables[var_name] = self.variable_counter
                self.variable_counter += 1
                return {
                    'type': 'not',
                    'subformula': {
                        'type': 'exists', 
                        'var': var_name, 
                        'subformula': {'type': 'not', 'subformula': self.build_ast(subformula)}}
                }
        elif formula.startswith('le'):
            # Use parenthesis-aware splitting
            if formula.startswith('le(') and formula.endswith(')'):
                inner = formula[3:-1]  # Remove 'le(' and ')'
                left, right = self._split_at_comma(inner)
                print(f"le with left: {left}, right: {right}")
                return {
                    'type': 'le',
                    'left': left,
                    'right': right
                }
        elif formula.startswith('¬'):
            if formula.startswith('¬(') and formula.endswith(')'):
                subformula = formula[2:-1].strip()  # Remove '¬(' and ')'
            else:
                subformula = formula[1:].strip()
            return {
                'type': 'not',
                'subformula': self.build_ast(subformula)
            }
        elif formula.startswith('and'):
            # Use parenthesis-aware splitting
            if formula.startswith('and(') and formula.endswith(')'):
                inner = formula[4:-1]  # Remove 'and(' and ')'
                left, right = self._split_at_comma(inner)
                print(f"and with left: {left}, right: {right}")
                return {
                    'type': 'and',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('or'):
            # Use parenthesis-aware splitting
            if formula.startswith('or(') and formula.endswith(')'):
                inner = formula[3:-1]  # Remove 'or(' and ')'
                left, right = self._split_at_comma(inner)
                print(f"or with left: {left}, right: {right}")
                return {
                    'type': 'or',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('->'):
            if formula.startswith('->(') and formula.endswith(')'):
                inner = formula[3:-1]  # Remove '->(' and ')'
                left, right = self._split_at_comma(inner)
                print(f"-> with left: {left}, right: {right}")
                return {
                    'type': 'implies',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('P_'):
            match = re.match(r'P_([a-zA-Z_]\w*)\((.*)\)', formula)
            if match:
                symbol = match.group(1).strip()
                var = match.group(2).strip()
                return {
                    'type': 'predicate',
                    'symbol': symbol,
                    'var': var
                }
        raise ValueError(f"Unrecognized formula: {formula}")
    
    def build_automaton(self, ast):
        """
        Convert an AST node to an automaton.
        """
        if ast['type'] == 'exists':
            var = ast['var']
            var_idx = self.bound_variables.get(var)
            sub_automaton = self.build_automaton(ast['subformula'])

            singleton = singl(var_idx, self.alphabet, self.k)
            combined = singleton.cut(sub_automaton)
            return combined
        
        elif ast['type'] == 'not':
            sub_automaton = self.build_automaton(ast['subformula'])
            return sub_automaton.complement()
        
        elif ast['type'] == 'le':
            left_var = ast['left']
            right_var = ast['right']
            left_idx = self.bound_variables.get(left_var)
            right_idx = self.bound_variables.get(right_var)
            return le(left_idx, right_idx, self.alphabet, self.k)
        
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
            return left_automaton.complement().union(right_automaton)
        
        elif ast['type'] == 'predicate':
            symbol = ast['symbol']
            var = ast['var']
            var_idx = self.bound_variables.get(var)
            return symb(symbol, var_idx, self.alphabet, self.k)


if __name__ == "__main__":
    alphabet = {'a', 'b'}
    k = 2
    parser = MSO_Parser(alphabet, k)
    formula = "∃x(∃y(and(le(x, y),P_a(x))))"
    ast = parser.build_ast(formula)
    print(ast)
    print(parser.bound_variables)
    automaton = parser.build_automaton(ast)

    projected = automaton.project(alphabet, k)
    det_proj = projected.determinize()

    test_inputs = ["","a","b", "aa", "ab", "ba", "bb", "aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb", "aaaab", "ababa", "bbaba", "bbaaa"
                "bbabb", "ababab","aaaaaaaaaaaaaaaaaaaaaaaaa"]
    for test_input in test_inputs:
        print(f"Input: {test_input}, Accepted: {det_proj.run(test_input)}")