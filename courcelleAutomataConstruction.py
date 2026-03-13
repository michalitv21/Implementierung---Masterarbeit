from treeAutomata import TreeAutomaton
from StringCase.utils import gen_courcelle_alphabet, gen_new_alphabet
from treeDecomp import Node, RootedTree

symbols = ["a", "b", "c", "d", "e", "f", "g"]
"""
Assume the alphabet is already in correct form
"""
def singl(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"s0", "s1", "sErr"},
        input_symbols=alphabet,
        final_states={"s1"},
        transitions={
            char: "s0" if char[i] == 0 else "s1"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "s0": {
                    "s0": "s0",
                    "s1": "s1",
                    "sErr": "sErr",
                },
                "s1": {
                    "s0": "s1",
                    "s1": "sErr",
                    "sErr": "sErr",
                },
                "sErr": {
                    "s0": "sErr",
                    "s1": "sErr",
                    "sErr": "sErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "s0": "s1" if char[i] == 1 else "s0",
                "s1": "sErr" if char[i] == 1 else "s1",
                "sErr": "sErr",
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def subset(i, j, alphabet, twd, k):
    # X1 <= X2
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"subAcc", "subErr"},
        input_symbols=alphabet,
        final_states={"subAcc"},
        transitions={
            # Leaf symbols (arity 0)
            char: "subErr" if char[i] == 1 and char[j] == 0
            else "subAcc"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            # // (arity 2): parallel composition — merge states from left and right child
            char: {
                "subAcc": {
                    "subAcc": "subAcc",
                    "subErr": "subErr",
                },
                "subErr": {
                    "subAcc": "subErr",
                    "subErr": "subErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            # miv_ (arity 1): if the miv symbol matches the state's symbol, go to sI
            char: {
                "subAcc" : "subErr" if char[i] == 1 and char[j] == 0 else "subAcc",
                "subErr": "subErr"
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def in1(i, j, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    aut_states = {"p0", "pOk", "pErr"} | {f"p_{x}" for x in symbols[:twd + 1]}
    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={"pOk"},
        transitions={
            char: "p0" if char[i] == 0 and char[j]== 0 else
                  "p_" + char[0][0] if char[i] == 1 and char[j] == 0 else
                   "pErr"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            # // (arity 2): parallel composition
            char: {
                s1: {
                    s2: s2 if s1 == "p0" else s1 if s2 == "p0" else "pErr"
                    for s2 in aut_states
                }
                for s1 in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            ## miv_ (arity 1):
            char: {
                q: q         if char[i] == 0 and char[j] == 0 and q != "p_" + char[0][-1]
                else "pOk"   if char[i] == 0 and char[j] == 1 and q == "p_" + char[0][-1]
                else "pErr"
                for q in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 1 #and char[0].startswith("miv_") no rename yet
        } 
    )
def in2(i, j, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    aut_states = {"p0", "pOk", "pErr"} | {f"p_{x}" for x in symbols[:twd + 1]}
    return TreeAutomaton(
        states=aut_states,
        input_symbols=alphabet,
        final_states={"pOk"},
        transitions={
            char: "p0" if char[i] == 0 and char[j]== 0 else
                  "p_" + char[0][1] if char[i] == 1 and char[j] == 0 else
                   "pErr"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            # // (arity 2): parallel composition
            char: {
                s1: {
                    s2: s2 if s1 == "p0" else s1 if s2 == "p0" else "pErr"
                    for s2 in aut_states
                }
                for s1 in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            # miv_ (arity 1):
            char: {
                q: q         if char[i] == 0 and char[j] == 0 and q != "p_" + char[0][-1]
                else "pOk"   if char[i] == 0 and char[j] == 1 and q == "p_" + char[0][-1]
                else "pErr"
                for q in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 1 #and char[0].startswith("miv_") no rename yet
        }
    )

def edges(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"s1", "sErr"},
        input_symbols=input_symbols,
        final_states={"s1"},
        transitions={
            char: "sErr" if char[i] == 1 and char[0].startswith("miv_") else "s1"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "s1": {
                    "s1": "s1",
                    "sErr": "sErr",
                },
                "sErr": {
                    "s1": "sErr",
                    "sErr": "sErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "s1": "sErr" if char[i] == 1 and char[0].startswith("miv_") else "s1",
                "sErr": "sErr",
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def vertices(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"s1", "sErr"},
        input_symbols=input_symbols,
        final_states={"s1"},
        transitions={
            char: "sErr" if char[i] == 1 and not (char[0].startswith("miv_")) else "s1"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "s1": {
                    "s1": "s1",
                    "sErr": "sErr",
                },
                "sErr": {
                    "s1": "sErr",
                    "sErr": "sErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "s1": "sErr" if char[i] == 1 and not (char[0].startswith("miv_")) else "s1",
                "sErr": "sErr",
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )