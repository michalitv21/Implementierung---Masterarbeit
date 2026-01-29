from treeAutomata import TreeAutomaton
from StringCase.utils import gen_new_alphabet
from treeDecomp import Node, RootedTree

def singl(i, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"s0", "s1", "s2"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"s1"},
        transitions={
            char: 
            {
                "s0": {
                    "s0": "s0" if char[i] == 0 else "s1",
                    "s1": "s1" if char[i] == 0 else "s2",
                    "s2": "s2",
                },
                "s1": {
                    "s0": "s1" if char[i] == 0 else "s2",
                    "s1": "s2",
                    "s2": "s2",
                },
                "s2": {
                    "s0": "s2",
                    "s1": "s2",
                    "s2": "s2",
                }
            } for char in new_alphabet if char[0] != 'leaf'
        } | {char: "s0" for char in new_alphabet if char[0] == 'leaf'}
    )

if __name__ == "__main__":
    alphabet = {
        "a":2, "b":2, "leaf":0
        }
    #print(gen_new_alphabet(alphabet, 2))
    s = singl(1, alphabet, 2)
    #print(s.input_symbols)
    print(s.transitions)

    n1 = Node(("leaf",0,1), 1, [])
    n2 = Node(("leaf",0,1), 2, [])
    n3 = Node(("a",1,0), 3, [n1,n2])

    tree = RootedTree(n3,[n1,n2,n3])

    s = singl(1, alphabet, 2)

    print(s.run(tree))