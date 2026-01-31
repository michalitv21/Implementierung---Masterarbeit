from treeDecomp import Node, RootedTree
from StringCase.utils import gen_new_alphabet

class TreeAutomaton:    
    def __init__(self, states, input_symbols, final_states, transitions):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.final_states = final_states
    
    # Tree must be ordered from leaves to root
    def nta_run(self, tree: RootedTree):
        state_dict = {}  # Maps each node to a list of all possible states
        #print(self.transitions)
        for node in tree.nodes:
            if node.label in self.input_symbols.keys():
                if self.input_symbols[node.label] == 0:
                    # Leaf node: collect all possible states
                    state = self.transitions[node.label]
                    if isinstance(state, list):
                        state_dict[node] = state  # Already a list of states
                    else:
                        state_dict[node] = [state]  # Wrap single state in a list
                elif self.input_symbols[node.label] == 1:
                    # Unary node: compute transitions for all child states
                    child_states_list = state_dict[node.children[0]]
                    possible_states = []
                    for child_state in child_states_list:
                        result = self.transitions[node.label][child_state]
                        if isinstance(result, list):
                            possible_states.extend(result)
                        else:
                            possible_states.append(result)
                    # Remove duplicates while preserving all unique states
                    state_dict[node] = list(set(possible_states))
                elif self.input_symbols[node.label] == 2:
                    # Binary node: compute transitions for all combinations of child states
                    child_states_list_0 = state_dict[node.children[0]]
                    child_states_list_1 = state_dict[node.children[1]]
                    possible_states = []
                    for child_state_0 in child_states_list_0:
                        for child_state_1 in child_states_list_1:
                            result = self.transitions[node.label][child_state_0][child_state_1]
                            if isinstance(result, list):
                                possible_states.extend(result)
                            else:
                                possible_states.append(result)
                    # Remove duplicates while preserving all unique states
                    state_dict[node] = list(set(possible_states))
                else:
                    # Handle higher arity nodes (generalized)
                    import itertools
                    child_states_lists = [state_dict[child] for child in node.children]
                    possible_states = []
                    for child_state_combination in itertools.product(*child_states_lists):
                        state = self.transitions[node.label]
                        for child_state in child_state_combination[:-1]:
                            state = state[child_state]
                        result = state[child_state_combination[-1]]
                        if isinstance(result, list):
                            possible_states.extend(result)
                        else:
                            possible_states.append(result)
                    # Remove duplicates while preserving all unique states
                    state_dict[node] = list(set(possible_states))
            else:
                print(node.label, " not in input symbols!")
                state_dict[node] = []
        
        #print("Final state dict: ", [{x.label: state_dict[x]} for x in state_dict.keys()])
        #print("Possible states at root: ", state_dict[tree.root])
        
        # Check if any of the possible states at the root is an accepting state
        return any(state in self.final_states for state in state_dict[tree.root])


    def run(self, tree: RootedTree):
        state_dict = {}
        #print(self.transitions)
        for node in tree.nodes:
            if node.label in self.input_symbols.keys():
                state = self.transitions[node.label]
                #print("Processing node: ", node)
                #print("Transition state (of char already): ", state)
                if self.input_symbols[node.label] > 0:
                    child_states = [state_dict[child] for child in node.children]
                    #print("Child states: ", child_states)
                    for i in range(len(child_states)-1):
                        #print("Child States i ", child_states[i])
                        state = state[child_states[i]]
                    # Get final transition result
                    result = state[child_states[-1]]
                    # Handle nondeterministic transitions (list of states) vs deterministic (single state)
                    if isinstance(result, list):
                        import random
                        state_dict[node] = random.choice(result)
                    else:
                        # Single state (could be a simple state or a tuple from union/cut)
                        state_dict[node] = result
                else:
                    # Leaf node: state is either a single state or a tuple from union/cut
                    if isinstance(state, list):
                        import random
                        state_dict[node] = random.choice(state)
                    else:
                        state_dict[node] = state

        
        # Check if any of the possible states at the root is an accepting state
        root_states = state_dict[tree.root]
        if isinstance(root_states, list):
            return any(state in self.final_states for state in root_states)
        else:
            return root_states in self.final_states
    
    def complement(self):
        new_final_states = self.states - self.final_states
        return TreeAutomaton(
            states=self.states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=self.transitions
        )
    
    def union(self, other):
        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        #print(new_states)
        new_final_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.final_states or s2 in other.final_states}
        #print(new_final_states)
        new_transitions = {}
        
        for char in self.input_symbols.keys():  # Assuming both automata have the same input symbols
            new_transitions[char] = {}
            if self.input_symbols[char] == 0:
                # Handle leaf transitions - combine states from both automata
                trans1 = self.transitions[char]
                trans2 = other.transitions[char]
                # Extract states from lists if present (nondeterministic case)
                states1 = trans1 if not isinstance(trans1, list) else trans1
                states2 = trans2 if not isinstance(trans2, list) else trans2
                # Create list of combined states
                combined = []
                if isinstance(states1, list) and isinstance(states2, list):
                    for s1 in states1:
                        for s2 in states2:
                            combined.append((s1, s2))
                elif isinstance(states1, list):
                    for s1 in states1:
                        combined.append((s1, states2))
                elif isinstance(states2, list):
                    for s2 in states2:
                        combined.append((states1, s2))
                else:
                    combined.append((states1, states2))
                new_transitions[char] = combined if len(combined) > 1 else combined[0] if combined else None
            elif self.input_symbols[char] == 1:
                pass
            else:
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    for (t1, t2) in new_states:
                        next_s1 = self.transitions[char][s1][t1]
                        next_s2 = other.transitions[char][s2][t2]
                        # Handle lists in transitions
                        if isinstance(next_s1, list) or isinstance(next_s2, list):
                            combined_next = []
                            states1 = next_s1 if isinstance(next_s1, list) else [next_s1]
                            states2 = next_s2 if isinstance(next_s2, list) else [next_s2]
                            for ns1 in states1:
                                for ns2 in states2:
                                    combined_next.append((ns1, ns2))
                            new_transitions[char][(s1, s2)][(t1, t2)] = combined_next if len(combined_next) > 1 else combined_next[0]
                        else:
                            new_transitions[char][(s1, s2)][(t1, t2)] = (next_s1, next_s2)
        #print("New Transitions: ",new_transitions)
        return TreeAutomaton(
            states=new_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )  

    def cut(self, other):
        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        #print(new_states)
        new_final_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.final_states and s2 in other.final_states}
        #print(new_final_states)
        new_transitions = {}
        
        for char in self.input_symbols.keys():  # Assuming both automata have the same input symbols
            new_transitions[char] = {}
            if self.input_symbols[char] == 0:
                # Handle leaf transitions - combine states from both automata
                trans1 = self.transitions[char]
                trans2 = other.transitions[char]
                # Extract states from lists if present (nondeterministic case)
                states1 = trans1 if not isinstance(trans1, list) else trans1
                states2 = trans2 if not isinstance(trans2, list) else trans2
                # Create list of combined states
                combined = []
                if isinstance(states1, list) and isinstance(states2, list):
                    for s1 in states1:
                        for s2 in states2:
                            combined.append((s1, s2))
                elif isinstance(states1, list):
                    for s1 in states1:
                        combined.append((s1, states2))
                elif isinstance(states2, list):
                    for s2 in states2:
                        combined.append((states1, s2))
                else:
                    combined.append((states1, states2))
                new_transitions[char] = combined if len(combined) > 1 else combined[0] if combined else None
            elif self.input_symbols[char] == 1:
                pass
            else:
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    for (t1, t2) in new_states:
                        next_s1 = self.transitions[char][s1][t1]
                        next_s2 = other.transitions[char][s2][t2]
                        # Handle lists in transitions
                        if isinstance(next_s1, list) or isinstance(next_s2, list):
                            combined_next = []
                            states1 = next_s1 if isinstance(next_s1, list) else [next_s1]
                            states2 = next_s2 if isinstance(next_s2, list) else [next_s2]
                            for ns1 in states1:
                                for ns2 in states2:
                                    combined_next.append((ns1, ns2))
                            new_transitions[char][(s1, s2)][(t1, t2)] = combined_next if len(combined_next) > 1 else combined_next[0]
                        else:
                            new_transitions[char][(s1, s2)][(t1, t2)] = (next_s1, next_s2)
        #print(new_transitions)
        return TreeAutomaton(
            states=new_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )  

    def project(self, alphabet, j, verbose=False):
        """
        Project away the LAST coordinate from tuple-based alphabet symbols.
        This removes the rightmost element representing set membership.
        Creates nondeterministic transitions when multiple symbols project to the same one.
        
        Args:
            alphabet: Set of base alphabet symbols (e.g., {'a', 'b'})
            j: Depth level for generating the new alphabet using gen_new_alphabet
            verbose: If True, print detailed debug output during projection
        
        Examples:
            ("b", 0, 1) → ("b", 0)
            ("b", 0) → "b"
        """

        if verbose:
            print("\n" + "="*70)
            print(f"STARTING PROJECTION (removing last coordinate)")
            print(f"Base alphabet: {alphabet}, depth level j={j}")
            print("="*70)
        
        new_input_symbols = {}
        new_transitions = {}
        
        # Determine the new alphabet based on projection depth
        if j - 1 == 0:
            # After projection, we're at the base alphabet level
            new_alphabet = alphabet
            if verbose:
                print(f"New alphabet (j=1): {new_alphabet}")
        else:
            # Generate new alphabet for projection depth j-1
            new_alphabet = gen_new_alphabet(alphabet, j - 1)
            if verbose:
                print(f"New alphabet (j={j}): {new_alphabet}")
        
        # Build mapping from old chars to new chars (removing LAST coordinate)
        char_mapping = {}
        if verbose:
            print(f"\nStep 1: Building character mapping (removing last coordinate)...")
        
        for old_char in self.input_symbols.keys():
            if isinstance(old_char, tuple):
                # Remove LAST element
                new_char = old_char[:-1]
                # If only one element left, unwrap the tuple
                if len(new_char) == 1:
                    new_char = new_char[0]
                char_mapping[old_char] = new_char
                if new_char in new_alphabet or (isinstance(new_char, tuple) and new_char in new_alphabet):
                    new_input_symbols[new_char] = self.input_symbols[old_char]
                    if verbose:
                        print(f"  {old_char} → {new_char} (arity: {self.input_symbols[old_char]})")
            else:
                # Not a tuple, keep as is if in new alphabet
                if old_char in new_alphabet:
                    char_mapping[old_char] = old_char
                    new_input_symbols[old_char] = self.input_symbols[old_char]
                    if verbose:
                        print(f"  {old_char} → {old_char} (unchanged, arity: {self.input_symbols[old_char]})")
        
        # Build new transitions by grouping old transitions that map to same new char
        if verbose:
            print("\nStep 2: Building new transitions...")
        for new_char in new_input_symbols.keys():
            arity = new_input_symbols[new_char]
            
            # Find all old chars that project to this new char
            old_chars_for_new = [oc for oc, nc in char_mapping.items() if nc == new_char]
            if verbose:
                print(f"\n  Processing '{new_char}' (arity={arity}):")
                print(f"    Old chars projecting to this: {old_chars_for_new}")
            
            if arity == 0:
                # Leaf transitions: collect all states from old chars
                collected_states = []
                for old_char in old_chars_for_new:
                    old_transition = self.transitions[old_char]
                    if verbose:
                        print(f"      From '{old_char}': {old_transition}")
                    if isinstance(old_transition, list):
                        collected_states.extend(old_transition)
                    else:
                        collected_states.append(old_transition)
                
                # Store as list if multiple states, single state otherwise
                if len(collected_states) > 1:
                    new_transitions[new_char] = collected_states
                    if verbose:
                        print(f"    → Result (nondeterministic): {collected_states}")
                elif len(collected_states) == 1:
                    new_transitions[new_char] = collected_states[0]
                    if verbose:
                        print(f"    → Result (deterministic): {collected_states[0]}")
            
            elif arity == 1:
                # Unary transitions
                new_transitions[new_char] = {}
                if verbose:
                    print(f"    Building unary transitions...")
                for state in self.states:
                    combined_results = []
                    for old_char in old_chars_for_new:
                        if state in self.transitions[old_char]:
                            result = self.transitions[old_char][state]
                            if isinstance(result, list):
                                combined_results.extend(result)
                            else:
                                combined_results.append(result)
                    
                    if len(combined_results) > 1:
                        new_transitions[new_char][state] = combined_results
                        if verbose:
                            print(f"      δ({state}) = {combined_results} (nondeterministic)")
                    elif len(combined_results) == 1:
                        new_transitions[new_char][state] = combined_results[0]
                        if verbose:
                            print(f"      δ({state}) = {combined_results[0]}")
            
            elif arity == 2:
                # Binary transitions
                new_transitions[new_char] = {}
                if verbose:
                    print(f"    Building binary transitions...")
                transition_count = 0
                for state1 in self.states:
                    new_transitions[new_char][state1] = {}
                    for state2 in self.states:
                        combined_results = []
                        for old_char in old_chars_for_new:
                            if state1 in self.transitions[old_char] and state2 in self.transitions[old_char][state1]:
                                result = self.transitions[old_char][state1][state2]
                                if isinstance(result, list):
                                    combined_results.extend(result)
                                else:
                                    combined_results.append(result)
                        
                        if len(combined_results) > 1:
                            new_transitions[new_char][state1][state2] = combined_results
                            transition_count += 1
                            if verbose and transition_count <= 5:  # Only print first few to avoid clutter
                                print(f"      δ({state1}, {state2}) = {combined_results} (nondeterministic)")
                        elif len(combined_results) == 1:
                            new_transitions[new_char][state1][state2] = combined_results[0]
                            transition_count += 1
                            if verbose and transition_count <= 5:
                                print(f"      δ({state1}, {state2}) = {combined_results[0]}")
                if verbose and transition_count > 5:
                    print(f"      ... and {transition_count - 5} more transitions")
        
        if verbose:
            print("\n" + "="*70)
            print("PROJECTION COMPLETE")
            print(f"New alphabet: {set(new_input_symbols.keys())}")
            print(f"States: {self.states}")
            print(f"Final states: {self.final_states}")
            print("="*70 + "\n")
        
        return TreeAutomaton(
            states=self.states,
            input_symbols=new_input_symbols,
            final_states=self.final_states,
            transitions=new_transitions
        )
