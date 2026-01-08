#Paper2
from graphLib import Graph, Vertex, permutationToTreeDecomposition
from treeDecomp import RootedTree, Tree, TreeDecomposition


v1 = Vertex("v1")
v2 = Vertex("v2")
v3 = Vertex("v3")
v4 = Vertex("v4")
v5 = Vertex("v5")
v6 = Vertex("v6")
v7 = Vertex("v7")
v8 = Vertex("v8")
v9 = Vertex("v9")
v10 = Vertex("v10")

graph2 = Graph([v1,v2,v3,v4,v5,v6,v7,v8,v9,v10],[{v1,v2},{v2,v3},{v7,v10},{v1,v3},{v1,v4},{v3,v4},{v4,v5},{v4,v7},{v4,v8},
                                                    {v5,v6},{v5,v9},{v6,v8},{v6,v9},{v7,v8},{v7,v9}, {v9,v10}])
graph2_copy = Graph(graph2.vertices.copy(), graph2.edges.copy())

tree = permutationToTreeDecomposition(graph2_copy, [v10, v9, v8, v7, v2, v3, v6, v1, v5, v4])
treeDecomp = TreeDecomposition(tree.I, tree)
print("Before rootedTree:")
print(treeDecomp)
print("After rootedTree:")
root_node = RootedTree.build_subtree(Tree(tree.I.copy(), tree.F.copy()), tree.I[v10], set())
print(root_node)