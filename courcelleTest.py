from StringCase.utils import gen_courcelle_alphabet
from courcelleAutomataConstruction import *

treewidth = 2
k = 3
alphabet = gen_courcelle_alphabet(treewidth, k)

print(alphabet)
print("------------------------------")
singl1_automaton = singl(1, alphabet, treewidth, k)
singl2_automaton = singl(2, alphabet, treewidth, k)
singl3_automaton = singl(3, alphabet, treewidth, k)
in1_automaton = in1(3, 1, alphabet, treewidth, k)
in2_automaton = in2(3, 2, alphabet, treewidth, k)
edges1_automaton = edges(1, alphabet, treewidth, k)
edges2_automaton = edges(2, alphabet, treewidth, k)
edges3_automaton = edges(3, alphabet, treewidth, k)
vertices1_automaton = vertices(1, alphabet, treewidth, k)
vertices2_automaton = vertices(2, alphabet, treewidth, k)
vertices3_automaton = vertices(3, alphabet, treewidth, k)

sub12_automaton = subset(1, 2, alphabet, treewidth, k)
#print(singl_automaton.states)
#print(singl_automaton.input_symbols)

#Quad Graph in F^HR given the belongings to the sets
b1 = Node(("ab", 0, 0, 0), 1, [])
b2 = Node(("bc", 0, 0, 0), 2, [])
b3 = Node(("ab", 0, 0, 0), 3, [])
b4 = Node(("bc", 0, 0, 1), 4, [])
b5 = Node("//", 6, [b1, b2])
b6 = Node("//", 7, [b3, b4])
b7 = Node(("miv_b", 0, 0, 0), 8, [b5])
b8 = Node(("miv_b", 1, 1, 0), 9, [b6])
b9 = Node("//", 10, [b7, b8])
b10 = Node(("miv_c", 0, 1, 0), 11, [b9])
b11 = Node(("miv_a", 0 ,0 ,0), 12, [b10])

tree_quad = RootedTree(b11, [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11])

#print(in1_automaton.transitions)

print("singl1(X1): ", singl1_automaton.nta_run(tree_quad))
print("------------------------------")
print("singl2(X2): ", singl2_automaton.nta_run(tree_quad))
print("------------------------------")
print("singl3(X3): ", singl3_automaton.nta_run(tree_quad))
print("------------------------------")

print("edges1(X1): ", edges1_automaton.nta_run(tree_quad))
print("------------------------------")
print("edges2(X2): ", edges2_automaton.nta_run(tree_quad))
print("------------------------------")
print("edges3(X3): ", edges3_automaton.nta_run(tree_quad))
print("------------------------------")

print("vertices1(X1): ", vertices1_automaton.nta_run(tree_quad))
print("------------------------------")
print("vertices2(X2): ", vertices2_automaton.nta_run(tree_quad))
print("------------------------------")
print("vertices3(X3): ", vertices3_automaton.nta_run(tree_quad))
print("------------------------------")

print("in1(X3, X1): ",in1_automaton.nta_run(tree_quad))
print("------------------------------")
print("in2(X3, X2): ",in2_automaton.nta_run(tree_quad))
print("------------------------------")
print("subset(X1, X2): ", sub12_automaton.nta_run(tree_quad))