




from treeDecomp import Node, RootedTree


class TreeAutomaton:    
    def __init__(self, states, input_symbols, final_states, transitions):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.final_states = final_states
    #Trees Node must be ordered: children before parents
    def evaluate(self, tree: RootedTree):
        state_dict = {}
        for node in tree.nodes:
            print(state_dict)
            if node.label in self.input_symbols:
                if node.is_leaf():
                    key = (node.label,)
                    possible_states = self.transitions.get(key, set())
                    state_dict[node] = possible_states
                else:
                    child_states_lists = [state_dict[child] for child in node.children]
                    possible_states = set()
                    from itertools import product
                    for child_states in product(*child_states_lists):
                        print(child_states)
                        key = (node.label,) + child_states
                        print(key)
                        possible_states.update(self.transitions.get(key, set()))
                    state_dict[node] = possible_states
            else:
                state_dict[node] = None
        return state_dict

if __name__ == "__main__":
    node1 = Node("0",1, [])
    node2 = Node("1", 2, [])
    node3 = Node("0", 3, [])
    node4 = Node("or", 4, [node1, node2])
    node5 = Node("1", 5, [])
    node6 = Node("not", 6, [node3])
    node7 = Node("not", 7, [node4])
    node8 = Node("or", 8, [node5, node6])
    node9 = Node("and", 9, [node7, node8])

    automaton = TreeAutomaton(
        states={"q0", "q1"},
        input_symbols={"0", "1", "and", "or", "not"},
        transitions={
            ("0",): {"q0"},
            ("1",): {"q1"},
            ("or", "q0", "q0"): {"q0"},
            ("or", "q0", "q1"): {"q1"},
            ("or", "q1", "q0"): {"q1"},
            ("or", "q1", "q1"): {"q1"},
            ("and", "q0", "q0"): {"q0"},
            ("and", "q0", "q1"): {"q0"},
            ("and", "q1", "q0"): {"q0"},
            ("and", "q1", "q1"): {"q1"},
            ("not", "q0"): {"q1"},
            ("not", "q1"): {"q0"},
        },
        final_states={"q1"}
    )

    print(RootedTree(node9, [node1, node2, node3, node4, node5, node6, node7, node8, node9]))
    result_states = automaton.evaluate(RootedTree(node9, [node1, node2, node3, node4, node5, node6, node7, node8, node9]))
    print("Possible states at root:", result_states[ node9 ])
    