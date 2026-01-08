from stringAutomata import Automaton


def gen_new_alphabet(alphabet, k):
    """
    Docstring for gen_new_alphabet
    
    :param alphabet: Symbols that are used
    :param k: Depth of Quantors

    Example: gen_new_alphabet({'a','b'}, 2) -> {('a',0,0), ('a',0,1), ('a',1,0), ('a',1,1), ('b',0,0), ('b',0,1), ('b',1,0), ('b',1,1)}
    """
    
    new_alphabet = set()
    for symbol in alphabet:
        def generate_tuples(current_tuple, depth):
            if depth == k:
                new_alphabet.add((symbol,) + current_tuple)
                return
            for i in range(2):
                generate_tuples(current_tuple + (i,), depth + 1)
        generate_tuples((), 0)
    return new_alphabet

def singl(i, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return Automaton(
        states={"q0", "q1"},
        alphabet=new_alphabet,
        start_states={"q0"},
        accept_states={"q1"},
        transitions={
            "q0": {x : "q0" for x in new_alphabet if x[i] == 0} | {x : "q1" for x in new_alphabet if x[i] == 1},
            "q1": {x : "q1" for x in new_alphabet if x[i] == 0}
        }
    )

def le(i,j, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return Automaton(
        states={"s0", "s1"},
        alphabet=new_alphabet,
        start_states={"s0"},
        accept_states={"s0","s1"},
        transitions={
            "s0": {x : "s0" for x in new_alphabet if x[j] == 1} | {x : "s1" for x in new_alphabet if x[j] == 0},
            "s1": {x : "s1" for x in new_alphabet if x[i] == 0}
        }
    )

def symb(char, i, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return Automaton(
        states={"p0", "p1"},
        alphabet=new_alphabet,
        start_states={"p0"},
        accept_states={"p0"},

        transitions={
            "p0": {x : "p1" if x[0] != char and x[i] == 1 else "p0" for x in new_alphabet}
        }


    )

def sub(i, j, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    return Automaton(
        states={"r0", "r1"},
        alphabet=new_alphabet,
        start_states={"r0"},
        accept_states={"r0"},

        transitions={
            "r0": {x : "r0" for x in new_alphabet if not (x[i] == 1 and x[j] == 0)} | {x : "r1" for x in new_alphabet if x[i] == 1 and x[j] == 0},
        }
    )

if __name__ == "__main__":
    alphabet = {'a', 'b'}
    k = 2
    #new_alphabet = gen_new_alphabet(alphabet, k)
    #print(new_alphabet)
    #print("Size of new alphabet: " + str(len(new_alphabet)))
    #single_automaton = singl(1, alphabet, k)
    #symb_a = symb('a', 1, alphabet, k)
    #print(symb_a.transitions)
    #print()

    #sub_12 = sub(1,2, alphabet, k)
    #print(sub_12.transitions)
    #print(sub_12.run([('a',1,0), ('b',0,1), ('a',0,1)]))

    # Formula: ∀x∃y (P_a(x) -> (P_b(y) ∧ x ≤ y)) | Didint work

    singl1 = singl(1, alphabet, k)
    print("Singl1 run: ", singl1.run([('a',1,0), ('b',0,1)]))

    singl2 = singl(2, alphabet, k)
    print("Singl2 run: ", singl2.run([('a',1,0), ('b',0,1)]))

    PaX1 = symb('a', 1, alphabet, k)
    print("PaX1 run: ", PaX1.run([('a',1,0), ('b',0,1)]))
    print("Symb a transitions: ", PaX1.transitions)

    PbX2 = symb('b', 2, alphabet, k)
    print("Symb b transitions: ", PbX2.transitions)
    print("PbX2 run: ", PbX2.run([('a',1,0), ('b',0,1)]))

    le12 = le(1,2, alphabet, k)
    print("le12 run: ", le12.run([('a',1,0), ('b',0,1)]))

    final_automaton = (((PbX2.cut(le12)).cut(PaX1)).cut(singl2)).cut(singl1)

    print(final_automaton.run([('a',1,0), ('b',1,1)]))  # Should be accepted