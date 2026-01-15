import re
from conversion import singl, le, symb, sub, Automaton
from stringAutomata import Automaton as StringAutomaton


class MSO_Parser:
    """
    Parser for Monadic Second-order Logic (MSO) formulas to Automata.
    
    Supports:
    - Existential quantifiers: ∃x, ∃X
    - Conjunction: ∧, and
    - Disjunction: ∨, or
    - Negation: ¬, not
    - Predicates: P_a(x), P_b(x), etc.
    - Relations: x ≤ y, x < y
    - Singleton checks: x ∈ S (for sets)
    """
    
    def __init__(self, alphabet, k):
        """
        Initialize the MSO parser.
        
        Args:
            alphabet: Set of symbols (e.g., {'a', 'b'})
            k: Depth of quantifiers (determines the dimension of extended alphabet)
        """
        self.alphabet = alphabet
        self.k = k
        self.variable_counter = {}
        self.bound_variables = {}  # Maps variable names to their indices
        
    def parse(self, formula: str) -> StringAutomaton:
        """
        Parse an MSO formula and return the corresponding automaton.
        
        Args:
            formula: MSO formula as string
            
        Returns:
            Automaton: The automaton corresponding to the formula
        """
        # Clean up the formula
        formula = formula.strip()
        
        # Parse quantifiers and the main formula
        ast = self._parse_formula(formula)
        
        # Convert AST to automaton
        automaton = self._ast_to_automaton(ast)
        
        return automaton
    
    def _parse_formula(self, formula: str):
        """
        Parse a formula string into an Abstract Syntax Tree (AST).
        
        Returns a dictionary representing the AST.
        """
        # Remove leading quantifiers and store variable bindings
        formula = formula.strip()
        quantifiers = []
        
        # Extract existential quantifiers
        while formula.startswith('∃') or formula.startswith('E'):
            match = re.match(r'[∃E]([a-zA-Z_]\w*)', formula)
            if match:
                var_name = match.group(1)
                #print(f"Found quantifier for variable: {var_name}")
                quantifiers.append(var_name)
                # Assign index to variable if not already assigned
                if var_name not in self.bound_variables:
                    self.bound_variables[var_name] = len(self.bound_variables) + 1
                formula = formula[match.end():]
            else:
                break
        
        formula = formula.strip()
        
        # Remove outer parentheses if present
        if formula.startswith('(') and formula.endswith(')'):
            formula = formula[1:-1]
        
        # Parse the inner formula
        expr = self._parse_expression(formula)
        
        # Wrap with quantifiers
        for var_name in reversed(quantifiers):
            expr = {
                'type': 'exists',
                'var': var_name,
                'body': expr
            }
        
        return expr
    
    def _parse_expression(self, expr: str):
        """
        Parse a logical expression (handles conjunctions, disjunctions, atoms).
        """
        expr = expr.strip()
        
        # Try to parse as conjunction first (lowest precedence)
        parts = self._split_by_operator(expr, ['∧', 'and'])
        if len(parts) > 1:
            result = self._parse_expression(parts[0])
            for part in parts[1:]:
                result = {
                    'type': 'and',
                    'left': result,
                    'right': self._parse_expression(part)
                }
            return result
        
        # Try to parse as disjunction
        parts = self._split_by_operator(expr, ['∨', 'or'])
        if len(parts) > 1:
            result = self._parse_expression(parts[0])
            for part in parts[1:]:
                result = {
                    'type': 'or',
                    'left': result,
                    'right': self._parse_expression(part)
                }
            return result
        
        # Try to parse as negation
        if expr.startswith('¬') or expr.startswith('not '):
            if expr.startswith('¬'):
                inner = expr[1:].strip()
            else:
                inner = expr[4:].strip()
            return {
                'type': 'not',
                'body': self._parse_expression(inner)
            }
        
        # Parse as atomic formula
        return self._parse_atom(expr)
    
    def _split_by_operator(self, expr: str, operators: list) -> list:
        """
        Split expression by operators while respecting parentheses.
        """
        depth = 0
        parts = []
        current = ""
        i = 0
        
        while i < len(expr):
            if expr[i] == '(':
                depth += 1
                current += expr[i]
            elif expr[i] == ')':
                depth -= 1
                current += expr[i]
            elif depth == 0:
                # Check for operators
                matched = False
                for op in operators:
                    if expr[i:i+len(op)] == op and (not op.isalpha() or i+len(op) >= len(expr) or not expr[i+len(op)].isalnum()):
                        parts.append(current.strip())
                        current = ""
                        i += len(op) - 1
                        matched = True
                        break
                if not matched:
                    current += expr[i]
            else:
                current += expr[i]
            
            i += 1
        
        if current.strip():
            parts.append(current.strip())
        
        return parts if len(parts) > 1 else [expr]
    
    def _parse_atom(self, atom: str):
        """
        Parse an atomic formula.
        
        Supports:
        - P_a(x): Predicate for symbol 'a' at position x
        - x ≤ y: Less than or equal relation
        - x < y: Less than relation
        - singl(i, ...): Singleton predicate
        - symb(char, i, ...): Symbol predicate
        - le(i, j, ...): Less than or equal relation
        """
        atom = atom.strip()
        
        # Check for predicate P_symbol(var)
        match = re.match(r'P_([a-zA-Z0-9_]+)\(([a-zA-Z_]\w*)\)', atom)
        if match:
            symbol = match.group(1)
            var = match.group(2)
            var_idx = self.bound_variables.get(var, 1)
            return {
                'type': 'symb',
                'symbol': symbol,
                'var': var,
                'var_idx': var_idx
            }
        
        # Check for relation x ≤ y or x <= y
        match = re.match(r'([a-zA-Z_]\w*)\s*(?:≤|<=)\s*([a-zA-Z_]\w*)', atom)
        if match:
            var1 = match.group(1)
            var2 = match.group(2)
            idx1 = self.bound_variables.get(var1, 1)
            idx2 = self.bound_variables.get(var2, 1)
            return {
                'type': 'le',
                'var1': var1,
                'var2': var2,
                'idx1': idx1,
                'idx2': idx2
            }
        
        # Check for relation x < y
        match = re.match(r'([a-zA-Z_]\w*)\s*<\s*([a-zA-Z_]\w*)', atom)
        if match:
            var1 = match.group(1)
            var2 = match.group(2)
            idx1 = self.bound_variables.get(var1, 1)
            idx2 = self.bound_variables.get(var2, 1)
            return {
                'type': 'sub',  # sub means var1 < var2
                'var1': var1,
                'var2': var2,
                'idx1': idx1,
                'idx2': idx2
            }
        
        # Check for singl(i, ...) format
        match = re.match(r'singl\((\d+)', atom)
        if match:
            idx = int(match.group(1))
            return {
                'type': 'singl',
                'idx': idx
            }
        
        # Check for symb(char, i, ...) format
        match = re.match(r"symb\('([^']+)',\s*(\d+)", atom)
        if match:
            char = match.group(1)
            idx = int(match.group(2))
            return {
                'type': 'symb_func',
                'char': char,
                'idx': idx
            }
        
        # Check for le(i, j, ...) format
        match = re.match(r'le\((\d+),\s*(\d+)', atom)
        if match:
            idx1 = int(match.group(1))
            idx2 = int(match.group(2))
            return {
                'type': 'le_func',
                'idx1': idx1,
                'idx2': idx2
            }
        
        raise ValueError(f"Unknown atomic formula: {atom}")
    
    def _ast_to_automaton(self, ast):
        """
        Convert an AST node to an automaton.
        """
        #print(ast)
        if ast['type'] == 'exists':
            # For existential quantification, we need to handle variable binding
            var = ast['var']
            var_idx = self.bound_variables.get(var, 1)
            
            body_automaton = self._ast_to_automaton(ast['body'])
            
            # Apply cut with singleton predicate for the variable
            singleton = singl(var_idx, self.alphabet, self.k)
            result = body_automaton.cut(singleton)
            
            return result
        
        elif ast['type'] == 'and':
            left_aut = self._ast_to_automaton(ast['left'])
            right_aut = self._ast_to_automaton(ast['right'])
            return left_aut.cut(right_aut)
        
        elif ast['type'] == 'or':
            left_aut = self._ast_to_automaton(ast['left'])
            right_aut = self._ast_to_automaton(ast['right'])
            return left_aut.union(right_aut)
        
        elif ast['type'] == 'not':
            body_aut = self._ast_to_automaton(ast['body'])
            return body_aut.complement()
        
        elif ast['type'] == 'symb':
            symbol = ast['symbol']
            var_idx = ast['var_idx']
            return symb(symbol, var_idx, self.alphabet, self.k)
        
        elif ast['type'] == 'le':
            idx1 = ast['idx1']
            idx2 = ast['idx2']
            return le(idx1, idx2, self.alphabet, self.k)
        
        elif ast['type'] == 'sub':
            idx1 = ast['idx1']
            idx2 = ast['idx2']
            return sub(idx1, idx2, self.alphabet, self.k)
        
        elif ast['type'] == 'singl':
            idx = ast['idx']
            return singl(idx, self.alphabet, self.k)
        
        elif ast['type'] == 'symb_func':
            char = ast['char']
            idx = ast['idx']
            return symb(char, idx, self.alphabet, self.k)
        
        elif ast['type'] == 'le_func':
            idx1 = ast['idx1']
            idx2 = ast['idx2']
            return le(idx1, idx2, self.alphabet, self.k)
        
        else:
            raise ValueError(f"Unknown AST node type: {ast['type']}")


def parse_mso(formula: str, alphabet, k) -> StringAutomaton:
    """
    Convenience function to parse an MSO formula.
    
    Args:
        formula: MSO formula as string
        alphabet: Set of symbols
        k: Quantifier depth
        
    Returns:
        Automaton: The corresponding automaton
    """
    parser = MSO_Parser(alphabet, k)
    return parser.parse(formula)


if __name__ == "__main__":
    alphabet = {'a', 'b'}
    k = 2
    
    # Test 1: Simple formula ∃x(P_a(x))
    print("Test 1: ¬∃x(P_a(x))")
    parser = MSO_Parser(alphabet, k)
    formula1 = "¬∃x(P_a(x))"
    print(f"Formula: {formula1}")
    try:
        aut1 = parser.parse(formula1)
        print("Parsed successfully!")
        print()
        # Project and determinize to test
        projected = aut1.project(alphabet, k)
        det_proj = projected.determinize()
        
        # Test some inputs
        test_inputs = ["ab","aa", "bb", "aab", "abb", "aabb", "ba", "bba"]
        print("Test results:")
        for test_input in test_inputs:
            result = det_proj.run(test_input)
            print(f"  Input: '{test_input}' => Accepted: {result}")
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Test 2: Two existential quantifiers ∃x∃y(P_a(x) ∧ P_b(y))
    print("Test 2: ∃x∃y(P_a(x) ∧ P_b(y))")
    parser = MSO_Parser(alphabet, k)
    formula2 = "∃x∃y(P_a(x) ∧ P_b(y))"
    print(f"Formula: {formula2}")
    try:
        aut2 = parser.parse(formula2)
        print("Parsed successfully!")
        print()
        # Project and determinize to test
        projected = aut2.project(alphabet, k)
        det_proj = projected.determinize()
        
        # Test some inputs
        test_inputs = ["ab","aa", "bb", "aab", "abb", "aabb", "ba", "bba"]
        print("Test results:")
        for test_input in test_inputs:
            result = det_proj.run(test_input)
            print(f"  Input: '{test_input}' => Accepted: {result}")
    except Exception as e:
        print(f"Error: {e}")
        print()
    