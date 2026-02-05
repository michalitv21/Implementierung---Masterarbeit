from utils import powerset, gen_new_alphabet
import random

class Automaton:
    def __init__(self, states, alphabet, start_states, accept_states:set, transitions:dict):
        self.states = states
        self.alphabet = alphabet
        self.start_states = start_states
        self.accept_states = accept_states if isinstance(accept_states, set) else set(accept_states)
        self.transitions = transitions  # dict of dicts: {state: {char: next_state}}

    def nfa_run(self, input_string:str):
        current_states = self.start_states
        #print("Running on input: " + str(input_string))
        #print("Start States: " + str(current_states))
        for char in input_string:
            #print("Current States: " + str(current_states))
            next_states = set()
            for state in current_states:
                if state in self.transitions and char in self.transitions[state]:
                    transition = self.transitions[state][char]
                    if isinstance(transition, list):
                        for t in transition:
                            if isinstance(t, tuple) and len(t) > 0 and isinstance(t[-1], list):
                                # Handle nested lists from cut operations
                                for nested_t in t[-1]:
                                    if isinstance(nested_t, (str, tuple)) and not isinstance(nested_t, list):
                                        next_states.add(nested_t)
                            elif isinstance(t, (str, tuple)) and not isinstance(t, list):
                                next_states.add(t)
                    elif isinstance(state, (str, tuple)) and not isinstance(state, list):
                        next_states.add(transition)
                    #print("Transition on '" + str(char) + "' from state " + str(state) + " to " + str(transition))
                else:
                    #print("No transition for '" + str(char) + "' from state " + str(state))
                    pass
            current_states = next_states
            #print("Next States after input '" + str(char) + "': " + str(current_states))

        return any(state in self.accept_states for state in current_states)

    def run(self, input_string:str):
        #print(len(self.start_states))
        if len(self.start_states) == 1:
            current_state = list(self.start_states)[0]
        else:
            #print("Nondeterministic start states, picking random start state.")
            current_state = random.choice(list(self.start_states))
        #print("Running on input: " + str(input_string))
        #print("Start State: " + str(current_state))
        for char in input_string:
            #print(current_state)
            if current_state in self.transitions and char in self.transitions[current_state]:
                if isinstance(self.transitions[current_state][char], list):
                    #print("Nondeterministic transition found, picking random option.")
                    current_state = random.choice(self.transitions[current_state][char])
                else:
                    current_state = self.transitions[current_state][char]
                    
                
                #print("Transition on '" + str(char) + "' to " + str(current_state))
            else:
                print("No transition for '" + str(char) + "' from state " + str(current_state))
                return False

        return current_state in self.accept_states

    def is_deterministic(self):
        if len(self.start_states) != 1:
            return False
        for state in self.states:
            for char in self.alphabet:
                if isinstance(self.transitions[state][char], list):
                    return False

        for state in self.states:
            if state in self.transitions:
                transitions_from_state = self.transitions[state]
                if transitions_from_state.keys() != self.alphabet:
                    return False
        return True

    
    def determinize(self):
        """
        Convert NFA to DFA using powerset construction.
        Uses frozensets to represent DFA states (sets of NFA states).
        Includes progress monitoring and detailed console output.
        """
        print("\n" + "="*70)
        print("STARTING DETERMINIZATION (Powerset Construction) of", self.transitions)
        print("="*70)
        
        # Step 1: Generate all possible subsets (powerset) of NFA states
        print(f"\nStep 1: Generating powerset of {len(self.states)} NFA states...")
        elems = list(self.states)
        new_states = set()
        
        # Calculate total subsets for progress tracking
        total_subsets = 2 ** len(elems)
        print(f"  → Total possible subsets: {total_subsets}")
        
        subset_count = 0
        for subset in powerset(elems):
            new_states.add(frozenset(subset))
            subset_count += 1
            # Show progress every 10% or for small sets
            if total_subsets <= 20 or subset_count % max(1, total_subsets // 10) == 0:
                progress = (subset_count / total_subsets) * 100
                bar_length = 30
                filled = int(bar_length * subset_count / total_subsets)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"\r  [{bar}] {progress:5.1f}% ({subset_count}/{total_subsets})                    ", end="", flush=True)
        
        print(f"\r  ✓ Generated {len(new_states)} DFA states (including empty set)                              ")
        
        # Step 2: Identify start states
        print(f"\nStep 2: Setting initial DFA state...")
        new_start_states = {frozenset(self.start_states)}
        print(f"  ✓ Initial state: {set(list(new_start_states)[0])}")
        
        # Step 3: Build transitions and identify accept states
        print(f"\nStep 3: Building transition function...")
        print(f"  Processing {len(new_states)} states × {len(self.alphabet)} symbols...")
        
        new_accept_states = set()
        new_transitions = {}
        state_count = 0
        total_states = len(new_states)
        
        for state in new_states:
            state_count += 1
            
            # Progress bar for state processing
            progress = (state_count / total_states) * 100
            bar_length = 30
            filled = int(bar_length * state_count / total_states)
            bar = "█" * filled + "░" * (bar_length - filled)
            state_display = str(set(state))[:50] if state else '∅'
            # Pad to 120 characters to ensure full line clearing
            output = f"  [{bar}] {progress:5.1f}% ({state_count}/{total_states}) | Current: {state_display}"
            print(f"\r{output:<120}", end="", flush=True)
            
            new_transitions[state] = {}
            
            # Process each alphabet symbol for this state
            for char in self.alphabet:
                next_states = set()
                
                # Collect all reachable states via char from any substate
                for substate in state:
                    if substate in self.transitions and char in self.transitions[substate]:
                        next_state = self.transitions[substate][char]
                        # Handle both single states and lists of states (for NFAs)
                        if isinstance(next_state, list):
                            for ns in next_state:
                                next_states.add(ns)
                        else:
                            next_states.add(next_state)
                
                # Store transition as frozenset
                new_transitions[state][char] = frozenset(next_states)
            
            # Check if this is an accept state (contains any NFA accept state)
            if any(substate in self.accept_states for substate in state):
                new_accept_states.add(state)
        
        print(f"\r  ✓ Transitions built for all {total_states} states                                        ")
        
        # Step 4: Summary
        print(f"\nStep 4: Creating DFA...")
        print(f"  ✓ Total DFA states: {len(new_states)}")
        print(f"  ✓ Accept states: {len(new_accept_states)}")
        print(f"  ✓ Transitions: {len(new_states)} states × {len(self.alphabet)} symbols")
        
        print("\n" + "="*70)
        print("DETERMINIZATION COMPLETE!")
        print("="*70 + "\n")
        
        return Automaton(new_states, self.alphabet, new_start_states, new_accept_states, new_transitions)        
    
    def complement(self):
        """
        print("Deterministic?: " + str(self.is_deterministic()))
        if not self.is_deterministic():
            self = self.determinize()
        """
        self = self.determinize()
        new_accept_states = self.states - self.accept_states
        return Automaton(self.states, self.alphabet, self.start_states, new_accept_states, self.transitions)

    def union(self, other):
        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        new_start_states = {(st1, st2) for st1 in self.start_states for st2 in other.start_states}
        new_accept_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.accept_states or s2 in other.accept_states}
        new_transitions = {}
        
        for (s1, s2) in new_states:
            new_transitions[(s1, s2)] = {}
            for char in self.alphabet.union(other.alphabet):
                next_s1 = self.transitions.get(s1, {}).get(char, s1)
                next_s2 = other.transitions.get(s2, {}).get(char, s2)
                if isinstance(next_s1, list) or isinstance(next_s2, list):
                    # Handle nondeterministic transitions by adding to list
                    combined_next_states = set()
                    if isinstance(next_s1, list):
                        combined_next_states.update(next_s1)
                    if isinstance(next_s2, list):
                        combined_next_states.update(next_s2)
                    
                else: new_transitions[(s1, s2)][char] = (next_s1, next_s2)
        
        return  Automaton(new_states, self.alphabet.union(other.alphabet), new_start_states, new_accept_states, new_transitions)

    def cut(self, other):

        #print("\n In Cut Method: \n")
        #print("Self Transitions: ", self.transitions)
        #print("Other Transitions: ", other.transitions)
        #print("\n End of Cut Method Print \n")

        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        new_start_states = {(st1, st2) for st1 in self.start_states for st2 in other.start_states}
        new_accept_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.accept_states and s2 in other.accept_states}
        new_transitions = {}
        
        for (s1, s2) in new_states:
            new_transitions[(s1, s2)] = {}
            for char in self.alphabet.union(other.alphabet):
                #print(f"Processiong transition for state ({s1}, {s2}) on char '{char}'")
                next_s1 = self.transitions.get(s1, {}).get(char)
                next_s2 = other.transitions.get(s2, {}).get(char)
                # If either side has no transition, this symbol is not allowed from the pair.
                if next_s1 is None or next_s2 is None:
                    continue
                #print(f"  Next states: {next_s1}, {next_s2}")
                if isinstance(next_s1, list) or isinstance(next_s2, list):
                    # Handle nondeterministic transitions by adding to list
                    #print(" Two NFAs in cut. Check implementation!!!")
                    combined_next_states = list()
                    if (isinstance(next_s1, list) and isinstance(next_s2, list)):
                        print(f"  Nondeterministic next states from both: {next_s1}, {next_s2}")
                        for ns1 in next_s1:
                            for ns2 in next_s2:
                                combined_next_states.append((ns1, ns2))

                    
                    elif isinstance(next_s1, list):
                        #print(f"  1. Nondeterministic next states from self: {next_s1}")
                        for ns1 in next_s1:
                            combined_next_states.append((ns1, next_s2))
                    elif isinstance(next_s2, list):
                        #print(f"  2. Nondeterministic next states from other: {next_s2}")  
                        for ns2 in next_s2:
                            combined_next_states.append((next_s1, ns2))
                
                    #print(f"  Combined next states (nondeterministic): {combined_next_states}")
                    new_transitions[(s1, s2)][char] = combined_next_states
                else: new_transitions[(s1, s2)][char] = (next_s1, next_s2)
        
        return Automaton(new_states, self.alphabet.union(other.alphabet), new_start_states, new_accept_states, new_transitions)

    def project(self, alphabet, j):
        #print(f"Projecting automaton to alphabet with depth {j}...")
        #print("Given transitions:", self.transitions)
        if (j - 1 == 0): 
            #print("In if case of projection.")
            #print("Given alphabet:", alphabet)
            new_alphabet = alphabet
            new_transitions = {}
            for transition in self.transitions:
                #print("Transition:", transition)
                #print(self.transitions[transition])
                new_transitions[transition] = {}
                for char in alphabet:
                    #print("char:", char)
                    new_transitions[transition][char] = list()
                    #print("self.transitions: ", self.transitions)
                    for old_char in self.transitions[transition]:
                        #print("old char:", old_char)
                        if old_char[0] == char:
                            next_state = self.transitions[transition][old_char]
                            if isinstance(next_state, list):
                                new_transitions[transition][char].extend(next_state)
                            else:
                                new_transitions[transition][char].append(next_state)
                    # Convert empty list to empty set (no transition)
                    if not new_transitions[transition][char]:
                        del new_transitions[transition][char]
        else:
            #print("In else case of projection.")
            new_alphabet = gen_new_alphabet(alphabet, j - 1)
            #print("New alphabet generated for projection.", new_alphabet)
            new_transitions = {}
            for transition in self.transitions:
                #print(transition)
                #print(self.transitions[transition])
                new_transitions[transition] = {}
                for char in new_alphabet:
                    new_transitions[transition][char] = list()
                    for old_char in self.transitions[transition]:
                        #print("#################", old_char[0:j], char[0:j])
                        if old_char[0:j] == char[0:j]:
                            new_transition = (char[0],)
                            for i in range(1, j+1):
                                if i != j:
                                    new_transition += (old_char[i],)
                            next_state = self.transitions[transition][old_char]
                            if new_transition not in new_transitions[transition]:
                                new_transitions[transition][new_transition] = list()
                            if isinstance(next_state, list):
                                new_transitions[transition][new_transition].extend(next_state)
                            else:
                                new_transitions[transition][new_transition].append(next_state)
                    # Clean up empty transitions
                    keys_to_remove = [k for k in new_transitions[transition] if not new_transitions[transition][k]]
                    for k in keys_to_remove:
                        del new_transitions[transition][k]
        #print("Projection complete. new transitions:", new_transitions)
        return Automaton(self.states, new_alphabet, self.start_states, self.accept_states, new_transitions)

                    

if __name__ == "__main__":
    ab = Automaton(
        states={"q0", "q1","qf"},
        alphabet={"a", "b"},
        start_states={"q0"},
        accept_states={"q1"},
        transitions={
            "q0": {"a": "q1",
                   "b": ["q0", "qf"]},
            "q1": {"b": "q0",
                   "a": "qf"},
            "qf": {"a": "qf",
                   "b": "qf"}
        })
    b = Automaton(
        states={"p0","pf"},
        alphabet={"a","b"},
        start_states={"p0"},
        accept_states={"p0"},
        transitions={
            "p0": {"a": "p0",
                    "b": "pf"},
            "pf": {"a": "pf",
                    "b": "pf"}
        })
    
    


    bstar = Automaton(
        states={"s0","sf"},
        alphabet={"a","b"},
        start_states={"s0"},
        accept_states={"s0"},
        transitions={
            "s0": {"a": "sf",
                    "b": "s0"},
            "sf": {"a": "sf",
                    "b": "sf"}
        })

    ab_union_b = ab.union(b)

    print("States: ", ab_union_b.states)
    print("Start States: ", ab_union_b.start_states)
    print("Accept States: ", ab_union_b.accept_states)
    print("Transitions: ", ab_union_b.transitions)
      
    ab_cut_b = ab.cut(b)

    print("Union Automaton Test:")

    test_strings = ["", "a", "b", "aa", "ab", "ba", "bb", "aab", "aba","bbb", "aaa", "aaaa", "abab", "baba", "abba", "bbbbb"]
    for s in test_strings:
        result = ab_union_b.run(s)
        print(f"Input: '{s}' => Accepted: {result}")


    print("States: ", ab_cut_b.states)
    print("Start States: ", ab_cut_b.start_states)
    print("Accept States: ", ab_cut_b.accept_states)
    print("Transitions: ", ab_cut_b.transitions)

    print("\nCut Automaton Test:")

    for s in test_strings:
        result = ab_cut_b.run(s)
        print(f"Input: '{s}' => Accepted: {result}")
    
    ab_cut_b_union_bstar = ab_cut_b.union(bstar)

    print("States: ", ab_cut_b_union_bstar.states)
    print("Start States: ", ab_cut_b_union_bstar.start_states)
    print("Accept States: ", ab_cut_b_union_bstar.accept_states)
    print("Transitions: ", ab_cut_b_union_bstar.transitions)

    print("\nCut then Union Automaton Test:")

    for s in test_strings:
        result = ab_cut_b_union_bstar.run(s)
        print(f"Input: '{s}' => Accepted: {result}")

    complement = ab_cut_b_union_bstar.complement()

    print("\nComplement Automaton Test:")
    for s in test_strings:
        result = complement.run(s)
        print(f"Input: '{s}' => Accepted: {result}")


    nfa = Automaton(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        start_states={"q0", "q1"},
        accept_states={"q2"},
        transitions={
            "q0": {"a": ["q0", "q1"],
                   "b": "q0"},
            "q1": {"a": "q2"},
            "q2": {"a": "q2",
                   "b": "q2"}
        })

    print("Is det?: " + str(nfa.is_deterministic()))  # Should be False

    det = nfa.determinize()  # Should print the new states after determinization
    print("Is det?: " + str(det.is_deterministic()))  # Should be True
    print("States: " + str(det.states))
    print("Start States: " + str(det.start_states))
    print("Accept States: " + str(det.accept_states))
    print("Transitions: " + str(det.transitions))

    test_strings_det = ["", "a", "b", "aa", "ab", "ba", "bb", "aab", "aba","bbb", "aaa", "aaaa", "abab", "baba", "abba", "bbbbb"]
    print("\nDeterminized Automaton Test:")
    for s in test_strings_det:
        result = det.run(s)
        print(f"Input: '{s}' => Accepted: {result}")


    nfa2 = Automaton(
        states={"p0", "p1", "pa", "pf"},
        alphabet={"a"},
        start_states={"p0", "p1"},
        accept_states={"pa"},
        transitions={
            "p0": {"a": ["pa", "p1"]},
            "p1": {"a": ["pa", "pf"]},
        })
    
    nfa2.run("aa")