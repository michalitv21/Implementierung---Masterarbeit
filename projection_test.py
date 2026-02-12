from treeAutomataConstruction import left, right, singl, symb, Node, RootedTree

alphabet = {
    "a":2,
    "b":2,
    "c":2,
    "d":1,
    "x":0,
    "y":0
}

t1n1 = Node("x", 1, [])
t1n2 = Node("x", 2, [])
t1n3 = Node("y", 3, [])
t1n4 = Node("y", 4, [])
t1n5 = Node("x", 5, [])
t1n6 = Node("y", 6, [])
t1n7 = Node("x", 7, [])
t1n8 = Node("y", 8, [])
t1n9 = Node("c", 9, [t1n1, t1n2])
t1n10 = Node("a", 10, [t1n3, t1n4])
t1n11 = Node("a", 11, [t1n5, t1n6])
t1n12 = Node("c", 12, [t1n7, t1n8])
t1n13 = Node("b", 13, [t1n9, t1n10])
t1n14 = Node("b", 14, [t1n11, t1n12])
t1n15 = Node("d", 15, [t1n13])
t1n16 = Node("d", 16, [t1n14])
t1n17 = Node("a", 17, [t1n15, t1n16])

t2n1 = Node("x", 1, [])
t2n2 = Node("x", 2, [])
t2n3 = Node("y", 3, [])
t2n4 = Node("y", 4, [])
t2n5 = Node("x", 5, [])
t2n6 = Node("y", 6, [])
t2n7 = Node("x", 7, [])
t2n8 = Node("y", 8, [])
t2n9 = Node("c", 9, [t2n1, t2n2])
t2n10 = Node("a", 10, [t2n3, t2n4])
t2n11 = Node("a", 11, [t2n5, t2n6])
t2n12 = Node("c", 12, [t2n7, t2n8])
t2n13 = Node("a", 13, [t2n9, t2n10])
t2n14 = Node("b", 14, [t2n11, t2n12])
t2n15 = Node("d", 15, [t2n13])
t2n16 = Node("d", 16, [t2n14])
t2n17 = Node("a", 17, [t2n15, t2n16])

tree1 = RootedTree(t1n17, [t1n1, t1n2, t1n3, t1n4, t1n5, t1n6, t1n7, t1n8, t1n9, t1n10, t1n11, t1n12, t1n13, t1n14, t1n15, t1n16, t1n17])

tree2 = RootedTree(t2n17, [t2n1, t2n2, t2n3, t2n4, t2n5, t2n6, t2n7, t2n8, t2n9, t2n10, t2n11, t2n12, t2n13, t2n14, t2n15, t2n16, t2n17])

symb_a_1 = symb("a", 1, alphabet, 2)
symb_b_2 = symb("b", 2, alphabet, 2)
symb_c_1 = symb("c", 1, alphabet, 2)
symb_y_2 = symb("y", 2, alphabet, 2)
singl1 = singl(1, alphabet, 2)
singl2 = singl(2, alphabet, 2)
left_21 = left(2,1, alphabet, 2)
right_21 = right(2,1, alphabet, 2)

#final_automaton = singl1.cut(singl2).cut((symb_a_1.cut(symb_b_2).cut(left_21)).union(symb_c_1.cut(symb_y_2).cut(right_21))).project(alphabet, 2).project(alphabet, 1)

final_automaton = singl1.cut(singl2).cut((symb_a_1.cut(symb_b_2)).cut(left_21).union(symb_c_1)).project(alphabet, 2).project(alphabet, 1)

print("One Path: " + str(final_automaton.run(tree1)))  # Should be accepted sometimes
print("One Path 2: " + str(final_automaton.run(tree2)))  # Should be accepted sometimes

print("All Paths: " + str(final_automaton.nta_run(tree1)))  # Should be accepted always
print("All Paths 2: " + str(final_automaton.nta_run(tree2)))  # Should be accepted always


dta_final_automaton = final_automaton.determinize_reachable()

print("DTA One Path: " + str(dta_final_automaton.run(tree1)))  # Should accepted always
print("DTA One Path 2: " + str(dta_final_automaton.run(tree2)))  # Should accepted always

#print("Transitions: " + str(final_automaton.transitions))
"""
res_list = []
for i in range(10000):
    res_list.append(final_automaton.run(tree))
print(res_list)
print(True in res_list)
"""
"""
from StringCase.utils import powerset

elems = list(final_automaton.states)
print("Input Symbols Powerset:")
for subset in powerset(elems):
    print(subset)
"""