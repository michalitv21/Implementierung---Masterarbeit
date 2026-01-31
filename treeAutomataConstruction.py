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
            } for char in new_alphabet if alphabet[char[0]] != 0
        } | {char: "s0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def sub(i, j, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"t0", "t1"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"t0"},
        transitions={
            char: 
            {
                "t1": {
                    "t0": "t1",
                    "t1": "t1",
                },
                "t0": {
                    "t0": "t1" if char[i] == 1 and char[j] == 0 else "t0",
                    "t1": "t1",
                }
            } for char in new_alphabet if alphabet [char[0]] != 0
        } | {char: "t0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def symb(symbol, i, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"p0", "p1"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"p0"},
        transitions={
            char: 
            {
                 "p1": {
                    "p0": "p1",
                    "p1": "p1",
                },
                "p0": {
                    "p0": "p1" if (not (char[0] == symbol)) and char[i] == 1 else "p0",
                    "p1": "p1",
                }
            } for char in new_alphabet if alphabet[char[0]] != 0
        } | {char: "p0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def left(i, j, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"l0", "l1", "l2", "l3"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"l3"},
        transitions={
            char: 
            {
                "l0": {
                    "l0": "l2" if char[i] == 1 and char[j] == 0 else "l0" if char[i] == 0 and char[j] == 0 else "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l3" if char[i] == 0 and char[j] == 0 else "l1",
                },
                "l1": {
                    "l0": "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l1"
                },
                "l2": {
                    "l0": "l3" if char[i] == 0 and char[j] == 1 else "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l1"
                },
                "l3": {
                    "l0": "l3" if char[i] == 0 and char[j] == 0 else "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l1"
                }
            } for char in new_alphabet if alphabet[char[0]] != 0
        } | {char: "l0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

if __name__ == "__main__":
    alphabet = {
        "a":2, "b":2, "leaf":0
        }
    #print(gen_new_alphabet(alphabet, 2))
    s = singl(1, alphabet, 2)
    sub_a = sub(1,2, alphabet, 2)
    #print(s.input_symbols)
    #print(s.transitions)

    symb_a_1 = symb("a", 1, alphabet, 2)
    symb_leaf_2 = symb("leaf", 2, alphabet, 2)
    left_1_2 = left(1,2, alphabet, 2)


    t1n1 = Node(("leaf", 0, 0), 1, [])
    t1n2 = Node(("leaf", 0, 0), 2, [])
    t1n3 = Node(("leaf", 0, 0), 3, [])
    t1n4 = Node(("leaf", 0, 0), 4, [])
    t1n5 = Node(("leaf", 0, 0), 5, [])
    t1n6 = Node(("leaf", 0, 0), 6, [])
    t1n7 = Node(("b", 1, 0), 7, [t1n1, t1n2])
    t1n8 = Node(("b", 0, 0), 8, [t1n3, t1n4])
    t1n9 = Node(("b", 0, 1), 9, [t1n7, t1n8])
    t1n10 = Node(("a", 0, 0), 10, [t1n5, t1n6])
    t1n11 = Node(("a", 0, 0), 11, [t1n9, t1n10])

    tree = RootedTree(t1n11, [t1n1, t1n2, t1n3, t1n4, t1n5, t1n6, t1n7, t1n8, t1n9, t1n10, t1n11])

    #s = singl(1, alphabet, 2)
    


    #print(symb_a_1.run(tree))
    #print(symb_leaf_2.run(tree))
    print(left_1_2.run(tree))