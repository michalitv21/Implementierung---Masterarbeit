from StringCase.utils import gen_courcelle_alphabet
from courcelleAutomataConstruction import *

treewidth = 2
k = 3
alphabet = gen_courcelle_alphabet(treewidth, k)

print(alphabet)

singl_automaton = singl(2, alphabet, treewidth, k)
sub_2_1_automaton = sub(2, 1, alphabet, treewidth, k)
#print(singl_automaton.states)
print(singl_automaton.input_symbols)

#Quad Graph in F^HR given the belongings to the sets
b1 = Node(("ab", "10", "01", "00"), 1, [])
b2 = Node(("bc", "01", "10", "00"), 2, [])
b3 = Node(("ab", "10", "00", "01"), 3, [])
b4 = Node(("bc", "10", "00", "01"), 4, [])
b5 = Node("//", 6, [b1, b2])
b6 = Node("//", 7, [b3, b4])
b7 = Node("miv_b", 8, [b5])
b8 = Node("miv_b", 9, [b6])
b9 = Node("//", 10, [b7, b8])
b10 = Node("miv_c", 11, [b9])
b11 = Node("miv_a", 12, [b10])

tree_quad = RootedTree(b11, [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11])

print(singl_automaton.nta_run(tree_quad))
print(sub_2_1_automaton.nta_run(tree_quad))