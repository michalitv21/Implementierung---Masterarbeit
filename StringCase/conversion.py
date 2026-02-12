from stringAutomata import Automaton
from utils import gen_new_alphabet

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
        states={"s0", "s1", "s_reject"},
        alphabet=new_alphabet,
        start_states={"s0"},
        accept_states={"s0","s1"},
        transitions={
            "s0": {x : "s0" for x in new_alphabet if x[j] == 0} | {x : "s1" for x in new_alphabet if x[j] == 1},
            "s1": {x : "s1" for x in new_alphabet if x[i] == 0} | {x : "s_reject" for x in new_alphabet if x[i] == 1},
            "s_reject": {x : "s_reject" for x in new_alphabet}
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


def build_in_automaton(set_idx, elem_idx, alphabet, k):
        new_alphabet = gen_new_alphabet(alphabet, k)
        
        # Create automaton that rejects only when elem_idx=1 and set_idx=0
        return Automaton(
            states={"q0", "q1"},
            alphabet=new_alphabet,
            start_states={"q0"},
            accept_states={"q0"},  # Accept in initial state
            transitions={
                "q0": {
                    x: "q0" if not (x[elem_idx] == 1 and x[set_idx] == 0) else "q1"
                    for x in new_alphabet
                },
                "q1": {x: "q1" for x in new_alphabet}  # Reject state (sink)
            }
        )

# WROOOONG! |a|=|b| is not definable in mso
def card_eq(set_idx_x, set_idx_y, alphabet, k):
    """
    Cardinality equality: |X| = |Y|
    Implemented as: X and Y contain exactly the same positions
    (This is sufficient for equal cardinality, though stronger)
    """
    new_alphabet = gen_new_alphabet(alphabet, k)
    
    return Automaton(
        states={"q0", "q1"},
        alphabet=new_alphabet,
        start_states={"q0"},
        accept_states={"q0"},  # Accept in initial state
        transitions={
            "q0": {
                x: "q0" if x[set_idx_x] == x[set_idx_y] else "q1"
                for x in new_alphabet
            },
            "q1": {x: "q1" for x in new_alphabet}  # Reject state
        }
    )

def even_set(set_idx, alphabet, k):
    new_alphabet = gen_new_alphabet(alphabet, k)
    
    return Automaton(
        states={"q0", "q1"},
        alphabet=new_alphabet,
        start_states={"q0"},
        accept_states={"q0"},  # Accept in initial state
        transitions={
            "q0": {
                x: "q1" if x[set_idx] == 1 else "q0"
                for x in new_alphabet
            },
            "q1": {
                x: "q0" if x[set_idx] == 1 else "q1"
                for x in new_alphabet
            }
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
    #print("Singl1 run: ", singl1.run([('a',1,0), ('b',0,1)]))

    singl2 = singl(2, alphabet, k)
    #print("Singl2 run: ", singl2.run([('a',1,0), ('b',0,1)]))

    PaX1 = symb('a', 1, alphabet, k)
    #print("PaX1 run: ", PaX1.run([('a',1,0), ('b',0,1)]))
    #print("Symb a transitions: ", PaX1.transitions)

    PbX2 = symb('b', 2, alphabet, k)
    #print("Symb b transitions: ", PbX2.transitions)
    #print("PbX2 run: ", PbX2.run([('a',1,0), ('b',0,1)]))

    le12 = le(1,2, alphabet, k)
    #print("le12 run: ", le12.run([('a',1,0), ('b',0,1)]))

    final_automaton = (((PbX2.cut(le12)).cut(PaX1)).cut(singl2)).cut(singl1)

    #print(final_automaton.run([('a',1,0), ('b',1,1)]))  # Should be accepted
    #print(final_automaton.transitions)
    #print(final_automaton.project(alphabet, k).transitions)

    #∃x(P_a(x))
    #aut = PaX1.cut(singl1) #Works!

    #∃x∃y(P_a(x) ∧ P_b(y))
    #aut = ((PbX2.cut(singl2)).cut(PaX1)).cut(singl1)

    #∃x∃y(P_a(x) ∧ P_b(y) ∧ x ≤ y)
    #exists(x,exists(y, and(P(a,x), and(P(b,y)), ≤(x, y)))))
    #exists(singl(X1))

    #aut = ((((PbX2.cut(le12)).cut(PaX1))).cut(singl2)).cut(singl1)

    #∀x(P_a(x))
    #∀X1(singl(X1) -> P_a(X1))
    #¬∃X1(¬(singl(X1) -> P_a(X1)))
    #¬∃X1(¬(¬singl(X1) ∨ P_a(X1)))
    #¬∃X1(singl(X1) ∧ ¬P_a(X1))
    print("Singl1 det: ",singl1.is_deterministic())
    print(singl1.transitions)
    print("PaX1 det: ",PaX1.is_deterministic())
    print("Comp det: ",(PaX1.complement()).is_deterministic())
    print("Singl1 cut Comp det: ",(singl1.cut(PaX1.complement())).is_deterministic())

    aut = singl1.cut(PaX1.complement())
    aut = aut.determinize()
    print("Final aut det: ",aut.is_deterministic())
    print(aut.accept_states)
    projected = aut.project(alphabet, k)
    det_proj_automaton = projected.determinize()
    det_proj_automaton = det_proj_automaton.complement()
    test_inputs = ["a","b", "aa", "ab", "ba", "bb", "aaa", "aab", "aba", "abb", "baa", "bab", "bba", "bbb", "aaaab", "ababa", "bbaba", "bbaaa"
                "bbabb", "ababab","aaaaaaaaaaaaaaaaaaaaaaaaa"]
    for test_input in test_inputs:
        print(f"Input: {test_input}, Accepted: {det_proj_automaton.run(test_input)}")

    #∃x∃y(P_a(x) ∧ P_b(y) ∧ x ≤ y)
    #∃x∃y(singl(1, alphabet, k) ∧ singl(2, alphabet, k) ∧ P_a(x) ∧ P_b(y) ∧ x ≤ y)
    #∃x∃y(and(singl(1, alphabet, k), and(singl(2, alphabet, k), and(symb('a',1, alphabet, k), and(symb('b',2, alphabet, k), le(1,2, alphabet, k))))))

    #evaluate(exists(x,exists(y, and(P('a',x), and(P('b',y)), ≤(x, y))))), {x:1, y:2})]
    #exists(and(singl(1, alphabet, k), and(singl(2, alphabet, k), and(symb('a',1, alphabet, k), and(symb('b',2, alphabet, k), le(1,2, alphabet, k))))))