#!/usr/bin/env python3
"""Quick test of tree decomposition"""
from graphLib import Graph, Vertex, minimal_degree_ordering, permutationToTreeDecomposition
from treeDecomp import TreeDecomposition

# Create a simple graph (triangle)
a = Vertex("a")
b = Vertex("b")
c = Vertex("c")

graph = Graph([a, b, c], [{a, b}, {b, c}, {a, c}])

print("Testing tree decomposition...")
print(f"Vertices: {[v.label for v in graph.vertices]}")
print(f"Edges: {graph.edges}")

# Get ordering
ordering = minimal_degree_ordering(graph)
print(f"Ordering: {[v.label for v in ordering]}")

# Create tree decomposition
td = permutationToTreeDecomposition(graph, ordering)
print(f"Tree decomposition created")
print(f"Bags: {td.I}")
print(f"Edges: {td.F}")

# Print bag details
for vertex, bag in td.I.items():
    print(f"  Bag '{bag.label}': vertices = {[str(v) for v in bag.vertices]}")

print("Test complete!")
