




from treeDecomp import Node, RootedTree


class TreeAutomaton:    
    def __init__(self, states, input_symbols, final_states, transitions):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.final_states = final_states
    
    # Tree must be ordered from leaves to root
    def run(self, tree: RootedTree):
        state_dict = {}
        for node in tree.nodes:
            if node.label in self.input_symbols.keys():
                if node.is_leaf():
                    key = node.label
                    state = self.transitions[key]
                    state_dict[node] = state
                elif self.input_symbols[node.label] == 1:
                    child_states = [state_dict[child] for child in node.children]
                    #print(transition_key)
                    state_dict[node] = self.transitions[node.label][child_states[0]]
                    #print(f"State dict[{node}]: ",state_dict[node])
                else:
                    child_states = [state_dict[child] for child in node.children]
                    #print(transition_key)
                    state_dict[node] = self.transitions[node.label][child_states[0]][child_states[1]]
                    #print(f"State dict[{node}]: ",state_dict[node])
            else:
                print(node.label, " not in input symbols!")
                state_dict[node] = None
        #print("State of root at end of run: ", state_dict[tree.root])
        return state_dict[tree.root] in self.final_states

    
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
                new_transitions[char] = (self.transitions[char], other.transitions[char])
            elif self.input_symbols[char] == 1:
                pass
            else:
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    for (t1, t2) in new_states:
                        next_s1 = self.transitions[char][s1][t1]
                        next_s2 = other.transitions[char][s2][t2]
                        new_transitions[char][(s1, s2)][(t1, t2)] = (next_s1, next_s2)
        #print(new_transitions)
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
                new_transitions[char] = (self.transitions[char], other.transitions[char])
            elif self.input_symbols[char] == 1:
                pass
            else:
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    for (t1, t2) in new_states:
                        next_s1 = self.transitions[char][s1][t1]
                        next_s2 = other.transitions[char][s2][t2]
                        new_transitions[char][(s1, s2)][(t1, t2)] = (next_s1, next_s2)
        #print(new_transitions)
        return TreeAutomaton(
            states=new_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )  

    