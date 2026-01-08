from utils import powerset

class DFAState:
    def __init__(self, nfa_states):
        self.states = frozenset(nfa_states)
    def __hash__(self):
        return hash(self.states)
    def __eq__(self, other):
        return self.states == other.states

class Automaton:
    def __init__(self, states, alphabet, start_states, accept_states:set, transitions:dict):
        self.states = states
        self.alphabet = alphabet
        self.start_states = start_states
        self.accept_states = accept_states if isinstance(accept_states, set) else set(accept_states)
        self.transitions = transitions  # dict of dicts: {state: {char: next_state}}

    def run(self, input_string:str):
        #print(len(self.start_states))
        if len(self.start_states) == 1:
            current_state = list(self.start_states)[0]
        else:
            current_state = None
        print("Running on input: " + str(input_string))
        print("Start State: " + str(current_state))
        for char in input_string:
            print(current_state)
            if current_state in self.transitions and char in self.transitions[current_state]:
                current_state = self.transitions[current_state][char]
                print("Transition on '" + str(char) + "' to " + str(current_state))
            else:
                print("No transition for '" + str(char) + "' from state " + str(current_state))
                return False

        return current_state in self.accept_states

    def is_deterministic(self):
        if len(self.start_states) != 1:
            return False
        for state in self.states:
            if state in self.transitions:
                transitions_from_state = self.transitions[state]
                if transitions_from_state.keys() != self.alphabet:
                    return False
        return True

    def determinize(self):
        elems = list(self.states)
        new_states = set()
        for subset in powerset(elems):
            new_states.add(frozenset(subset))
        print("New States: " + str(new_states))
        new_start_states = {frozenset(self.start_states)}
        new_accept_states = set()
        new_transitions = {}
        for state in new_states:
           new_transitions[state] = {}
           for char in self.alphabet:
                next_states = set()
                for substate in state:
                    if substate in self.transitions and char in self.transitions[substate]:
                        next_state = self.transitions[substate][char]
                        if isinstance(next_state, list):
                            for ns in next_state:
                                next_states.add(ns)
                        else:
                            next_states.add(next_state)
                new_transitions[state][char] = frozenset(next_states)
                if any(substate in self.accept_states for substate in state):
                    new_accept_states.add(state)
        return Automaton(new_states, self.alphabet, new_start_states, new_accept_states, new_transitions)        
    
    def complement(self):
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
                new_transitions[(s1, s2)][char] = (next_s1, next_s2)
        
        return  Automaton(new_states, self.alphabet.union(other.alphabet), new_start_states, new_accept_states, new_transitions)

    def cut(self, other):
        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        new_start_states = {(st1, st2) for st1 in self.start_states for st2 in other.start_states}
        new_accept_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.accept_states and s2 in other.accept_states}
        new_transitions = {}
        
        for (s1, s2) in new_states:
            new_transitions[(s1, s2)] = {}
            for char in self.alphabet.union(other.alphabet):
                next_s1 = self.transitions.get(s1, {}).get(char, s1)
                next_s2 = other.transitions.get(s2, {}).get(char, s2)
                new_transitions[(s1, s2)][char] = (next_s1, next_s2)
        
        return Automaton(new_states, self.alphabet.union(other.alphabet), new_start_states, new_accept_states, new_transitions)

if __name__ == "__main__":
    ab = Automaton(
        states={"q0", "q1","qf"},
        alphabet={"a", "b"},
        start_states={"q0"},
        accept_states={"q1"},
        transitions={
            "q0": {"a": "q1",
                   "b": "qf"},
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