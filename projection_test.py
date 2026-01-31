from treeAutomataConstruction import left, singl, symb, Node, RootedTree

alphabet = {
    "a":2,
    "b":2,
    "leaf":0
}

t1n1 = Node("leaf", 1, [])
t1n2 = Node("leaf", 2, [])
t1n3 = Node("leaf", 3, [])
t1n4 = Node("leaf", 4, [])
t1n5 = Node("leaf", 5, [])
t1n6 = Node("leaf", 6, [])
t1n7 = Node("b", 7, [t1n1, t1n2])
t1n8 = Node("b", 8, [t1n3, t1n4])
t1n9 = Node("b", 9, [t1n7, t1n8])
t1n10 = Node("a", 10, [t1n5, t1n6])
t1n11 = Node("a", 11, [t1n9, t1n10])
tree = RootedTree(t1n11, [t1n1, t1n2, t1n3, t1n4, t1n5, t1n6, t1n7, t1n8, t1n9, t1n10, t1n11])

symb_b_1 = symb("b", 1, alphabet, 2)
symb_a_2 = symb("a", 2, alphabet, 2)
singl1 = singl(1, alphabet, 2)
singl2 = singl(2, alphabet, 2)
left_12 = left(1,2, alphabet, 2)

final_automaton = ((((symb_a_2.cut(left_12)).cut(symb_b_1)).cut(singl2)).cut(singl1).project(alphabet, 2)).project(alphabet, 1)

print("One Path: " + str(final_automaton.run(tree)))  # Should be accepted sometimes

print("All Paths: " + str(final_automaton.nta_run(tree)))  # Should be accepted always
"""
res_list = []
for i in range(10000):
    res_list.append(final_automaton.run(tree))
print(res_list)
print(True in res_list)
"""