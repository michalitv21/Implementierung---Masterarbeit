from treeAutomata import TreeAutomaton
from StringCase.utils import gen_new_alphabet
from treeDecomp import Node, RootedTree

symbols = ["a", "b", "c", "d", "e", "f", "g"]
"""
Assume the alphabet is already in correct form
"""
def singl(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = alphabet
    return TreeAutomaton(
        states={"s0", "sI", "sErr"} | {f"s{s}" for s in symbols[:twd+1]},
        input_symbols=alphabet,
        final_states={"sI"},
        transitions={
            # Leaf symbols (arity 0): edge introductions like ("ab", "00", "01")
            char: "s0" if char[i] == "00"
                  else "s" + char[0][0] if char[i] == "10"
                  else "s" + char[0][1] if char[i] == "01"
                  else "sErr"
            for char in input_symbols.keys() if alphabet[char] == 0
        } | {
            # // (arity 2): parallel composition — merge states from left and right child
            char: {
                s1: {
                    s2: "sErr" if s1 == "sErr" or s2 == "sErr"
                        else "sErr" if s1 != "s0" and s2 != "s0" and s1 != s2
                        else s1 if s2 == "s0"
                        else s2
                    for s2 in {"s0", "sI", "sErr"} | {f"s{s}" for s in symbols[:twd+1]}
                }
                for s1 in {"s0", "sI", "sErr"} | {f"s{s}" for s in symbols[:twd+1]}
            }
            for char in input_symbols.keys() if alphabet[char] == 2
        } | {
            # miv_ (arity 1): if the miv symbol matches the state's symbol, go to sI
            char: {
                "s0": "s0",
                "sI": "sI",
                "sErr": "sErr",
                **{
                    "s" + x: "sI" if x == char[-1] else "s" + x for x in symbols[:twd+1]
                },
            } for char in input_symbols.keys() if alphabet[char] == 1 and char.startswith("miv_")
        } | {
            # ren_ (arity 1): rename symbol, e.g. ren_ab renames a->b in the state
            char: {
                "s0": "s0",
                "sI": "sI",
                "sErr": "sErr",
                **{
                    "s" + x: "s" + char[-1] if x == char[-2] else "s" + x for x in symbols[:twd+1]
                },
            } for char in input_symbols.keys() if alphabet[char] == 1 and char.startswith("ren_")
        }
    )

def sub(i, j, alphabet, twd, k):
    input_symbols = alphabet
    return TreeAutomaton(
        states={"subAcc", "subErr"},
        input_symbols=alphabet,
        final_states={"subAcc"},
        transitions={
            # Leaf symbols (arity 0): edge introductions like ("ab", "00", "01")
            char: "subErr" if char[i][0] == "1" and char[j][0] == "0" 
                            or char[i][1] == "1" and char[j][1] == "0"
            else "subAcc"
            for char in input_symbols.keys() if alphabet[char] == 0
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
            for char in input_symbols.keys() if alphabet[char] == 2
        } | {
            # miv_ (arity 1): if the miv symbol matches the state's symbol, go to sI
            char: {
                "subAcc" : "subAcc",
                "subErr": "subErr"
            } for char in input_symbols.keys() if alphabet[char] == 1
        }
    )

#Assuming sets are singletons, so that the edge is between the two vertices
def adj(i,j, alphabet, twd, k):
    input_symbols = alphabet
    return TreeAutomaton(
        states={"subAcc", "subErr"},
        input_symbols=alphabet,
        final_states={"subAcc"},
        transitions={
            # Leaf symbols (arity 0): edge introductions like ("ab", "00", "01")
            char: "subErr" if char[i][0] == "1" and char[j][0] == "0" 
                            or char[i][1] == "1" and char[j][1] == "0"
            else "subAcc"
            for char in input_symbols.keys() if alphabet[char] == 0
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
            for char in input_symbols.keys() if alphabet[char] == 2
        } | {
            # miv_ (arity 1): if the miv symbol matches the state's symbol, go to sI
            char: {
                "subAcc" : "subAcc",
                "subErr": "subErr"
            } for char in input_symbols.keys() if alphabet[char] == 1
        }
    )