from treeAutomata import TreeAutomaton
from StringCase.utils import gen_new_alphabet
from treeDecomp import Node, RootedTree

def singl(i, alphabet, k):
    print("Constructing singl automaton for position ", i)
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
    print("Constructing sub automaton for positions ", i, " and ", j)
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
    print("Constructing symb automaton for symbol ", symbol, " at position ", i)
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
    print("Constructing left automaton for positions ", i, " and ", j)
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

def right(i, j, alphabet, k):
    print("Constructing right automaton for positions ", i, " and ", j)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"r0", "r1", "r2", "r3"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"r3"},
        transitions={
            char: 
            {
                "r0": {
                    "r0": "r2" if char[j] == 1 and char[i] == 0 else "r0" if char[j] == 0 and char[i] == 0 else "r1",
                    "r1": "r1",
                    "r2": "r3" if char[i] == 0 and char[j] == 1 else "r1",
                    "r3": "r3" if char[j] == 0 and char[i] == 0 else "r1",
                },
                "r1": {
                    "r0": "r1",
                    "r1": "r1",
                    "r2": "r1",
                    "r3": "r1"
                },
                "r2": {
                    "r0": "r1",
                    "r1": "r1",
                    "r2": "r1",
                    "r3": "r1"
                },
                "r3": {
                    "r0": "r3" if char[j] == 0 and char[i] == 0 else "r1",
                    "r1": "r1",
                    "r2": "r1",
                    "r3": "r1"
                }
            } for char in new_alphabet if alphabet[char[0]] != 0
        } | {char: "r0" for char in new_alphabet if alphabet[char[0]] == 0}
    )