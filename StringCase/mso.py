import re
from conversion import card_eq, singl, le, symb, sub, build_in_automaton, Automaton
from stringAutomata import Automaton as StringAutomaton

class MSO_Parser:

    def __init__(self, alphabet, k):
        self.alphabet = alphabet
        self.k = k
        self.variable_counter = 1
        self.bound_variables = {}
        self.variable_types = {}

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
            fo_match = re.match(r'∃([a-z_]\w*)\((.*)\)', formula)
            so_match = re.match(r'∃([A-Z_]\w*)\((.*)\)', formula)
            quant_match = fo_match or so_match
            if quant_match:
                var_name = quant_match.group(1).strip()
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
        # in the case of universal quantification we replace it with negated existential (∀x:f -> ¬∃x:¬f)
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
                        'subformula': {'type': 'not', 'subformula': self.build_ast(subformula)}
                    }
                }
        elif formula.startswith('le'):
            # Use parenthesis-aware splitting
            if formula.startswith('le(') and formula.endswith(')'):
                inner = formula[3:-1]  # Remove 'le(' and ')'
                left, right = self._split_at_comma(inner)
                #print(f"le with left: {left}, right: {right}")
                return {
                    'type': 'le',
                    'left': left,
                    'right': right
                }
        elif formula.startswith('not'):
            if formula.startswith('not(') and formula.endswith(')'):
                subformula = formula[4:-1].strip()  # Remove 'not(' and ')'
            else:
                subformula = formula[3:].strip()
            return {
                'type': 'not',
                'subformula': self.build_ast(subformula)
            }
        elif formula.startswith('and'):
            # Use parenthesis-aware splitting
            if formula.startswith('and(') and formula.endswith(')'):
                inner = formula[4:-1]  # Remove 'and(' and ')'
                left, right = self._split_at_comma(inner)
                #print(f"and with left: {left}, right: {right}")
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
                #print(f"or with left: {left}, right: {right}")
                return {
                    'type': 'or',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('->'):
            if formula.startswith('->(') and formula.endswith(')'):
                inner = formula[3:-1]  # Remove '->(' and ')'
                left, right = self._split_at_comma(inner)
                #print(f"-> with left: {left}, right: {right}")
                return {
                    'type': 'implies',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('in'):
            # Parse in(X,x) where X is second-order, x is first-order
            if formula.startswith('in(') and formula.endswith(')'):
                inner = formula[3:-1]  # Remove 'in(' and ')'
                set_var, elem_var = self._split_at_comma(inner)
                return {
                    'type': 'in',
                    'set_var': set_var,
                    'elem_var': elem_var
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
        elif formula.startswith("card_eq"):
            if formula.startswith('card_eq(') and formula.endswith(')'):
                inner = formula[8:-1]  # Remove 'card_eq(' and ')'
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'card_eq',
                    'left': left,
                    'right': right
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
        """
        Convert an AST node to an automaton.
        """
        if ast['type'] in ('exists', 'exists_first'):
            var = ast['var']
            var_idx = self.bound_variables.get(var)
            # DO NOT decrement k before recursion - keep it the same
            sub_automaton = self.build_automaton(ast['subformula'])
            
            #print("Subautomaton transitions:", sub_automaton.transitions)

            singleton = singl(var_idx, self.alphabet, self.k)

            #print("Singleton transitions:", singleton.transitions)

            combined = singleton.cut(sub_automaton)

            #print("Cut Automaton transitions:", combined.transitions)

            automaton = combined.project(self.alphabet, var_idx)
            #print("Automaton alphabet: ",automaton.alphabet)
            #print("Projected Automaton transitions:", automaton.transitions)
            self.k = self.k-1
            return automaton
        
        elif ast['type'] == 'exists_second':
            var = ast['var']
            var_idx = self.bound_variables.get(var)
            sub_automaton = self.build_automaton(ast['subformula'])
            automaton = sub_automaton.project(self.alphabet, var_idx)
            self.k = self.k-1
            return automaton
        
        elif ast['type'] == 'not':
            sub_automaton = self.build_automaton(ast['subformula'])
            return sub_automaton.complement()
        
        elif ast['type'] == 'le':
            left_var = ast['left']
            right_var = ast['right']
            left_idx = self.bound_variables.get(left_var)
            right_idx = self.bound_variables.get(right_var)
            #print(f"Building le automaton for indices: {left_idx}, {right_idx}" )
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
        
        elif ast['type'] == 'in':
            # in(X,x): position x must be in set X
            set_var = ast['set_var']
            elem_var = ast['elem_var']
            set_idx = self.bound_variables.get(set_var)
            elem_idx = self.bound_variables.get(elem_var)
            #print(f"Building in automaton for set_idx: {set_idx}, elem_idx: {elem_idx}")
            return build_in_automaton(set_idx, elem_idx, self.alphabet, self.k)
        
        elif ast['type'] == 'predicate':
            symbol = ast['symbol']
            var = ast['var']
            var_idx = self.bound_variables.get(var)
            return symb(symbol, var_idx, self.alphabet, self.k)

        elif ast['type'] == 'card_eq':
            left_var = ast['left']
            right_var = ast['right']
            left_idx = self.bound_variables.get(left_var)
            right_idx = self.bound_variables.get(right_var)
            return card_eq(left_idx, right_idx, self.alphabet, self.k)

if __name__ == "__main__":
    alphabet = {'a', 'b'}
    k = 3
    parser = MSO_Parser(alphabet, k)
    #formula = "∃x(∃y(and(le(x,y),and(P_a(x),P_b(y)))))"
    #formula = "∃x(not(∃y(and(P_a(x),and(P_a(y),le(x,y))))))"
    #formula = "∃x(∃y(∃z(and(and(P_a(x),P_a(y)),and(le(y, z), P_b(z))))))"
    #formula = "∀x(∃y(->(P_a(x),and(P_b(y),le(x,y)))))"
    #formula = "∃X(∃x(and(in(X,x), not(∃y(and(le(y,x), not(and(le(x,y), le(y,x)))))))))"
    #formula = "∃x(∃y(and(P_a(x), P_b(y))))"
    #formula = "∃x(∀Z(->(and(P_c(x),in(Z,x))))"
    #formula = "∃X(∃Y(∃x(∃y(∃z(and(and(in(X,x),in(Y,y)),and(and(in(X,x),le(x,y)),le(y,z))))))))"
    formula = "∃x(∃y(∃z(and(and(le(x,y),le(y,z)),and(P_a(x),and(P_b(y),P_a(z)))))))"
    # |a| = |b|
    #formula = "∃X(∃Y(∀x(∀y( and( <->(P_a(x),in(X,x)) , and( <->(P_b(y),in(Y,y)) , card_eq(X,Y) ) ) ))))"

    ast = parser.build_ast(formula)
    print(ast)
    print(parser.bound_variables)
    automaton = parser.build_automaton(ast)
    #print("Automaton alphabet:", automaton.alphabet)
    #print("Automaton transitions:", automaton.transitions)
    #projected = automaton.project(alphabet, 2)
    #projected = automaton.project(alphabet, 1)
    #print("Projected transitions:" , projected.transitions)
    
    #print(automaton.transitions)
    #det_proj = automaton.determinize()

    test_inputs = ["","a","b", "aa", "ab", "ba", "bb", "aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb", "aaaab", "ababa", "bbaba", "bbaaa"
                "bbabb", "ababab","aaaaaaaaaaaaaaaaaaaaaaaaa"]
    for test_input in test_inputs:
        print(f"Input: {test_input}, Accepted: {automaton.nfa_run(test_input)}")
        