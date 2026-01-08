
class Bag:
    def __init__(self, label:str, vertices:set):
        self.label = label
        self.vertices = vertices if isinstance(vertices, set) else set(vertices)
        
        
    def add_vertex(self, v):
        self.vertices.add(v)

    def __repr__(self):
        return str(self.vertices)

class Tree:
    def __init__(self, I, F):
        self.I = I
        self.F = F

    def __str__(self):
        return "bags: " + str(self.I) +"\nedges: " + str(self.F)

    def __repr__(self):
        return "bags: " + str(self.I) +"\nedges: " + str(self.F)

    def add_edge(self, b1:Bag, b2:Bag):
        self.F.append(set([b1,b2]))


class TreeDecomposition:
    def __init__(self, bags, tree:Tree):
        self.bags = bags
        self.tree = tree

    def __str__(self):
        return "bags: " + str(self.bags) +"\nedges: " + str(self.tree.F)

    def __repr__(self):
        return "bags: " + str(self.bags) +"\nedges: " + str(self.tree.F)
    
    def combine_bags(self, into, remove):
        # Combine the vertices of remove into into
        into.vertices = into.vertices.union(remove.vertices)
        # Update tree edges
        for e in self.tree.F.copy():
            if remove in e:
                other_bag = (e - set([remove])).pop()
                self.tree.F.remove(e)
                if other_bag != into:
                    self.tree.add_edge(into, other_bag)
        # Remove the bag
        if remove in self.bags:
            self.bags.remove(remove)
        if remove in self.tree.I:
            del self.tree.I[remove.label]

class Node():
    def __init__(self, label, id, children:list):
        self.label = label
        self.id = id
        self.children = children

    def __str__(self):
        return (self.label + "(" + ", ".join([str(c) for c in self.children]) + ")")
        #label is Bag then we need the label of the bag

    def add_child(self, child:Node):
        self.children.append(child)
    
    def remove_child(self, child:Node):
        self.children.remove(child)

    def is_leaf(self):
        return len(self.children) == 0



class RootedTree():
    def __init__(self, root:Node, nodes):
        self.root = root
        self.nodes = nodes
        # Add contruction of tree with parent - children relation
    def __str__(self):
        return str(self.root)

    def __repr__(self):
        return str(self.root)
    
    def add_node(self, node:Node):  
        self.nodes.append(node)

    def set_root(self, root:Node):
        self.root = root
    
    def build_subtree(tree:Tree, bag:Bag, visited:set):
        visited.add(bag)
        node = Node(bag, [])
        for edge in tree.F:
            if bag in edge:
                other_bag = (edge - set([bag])).pop()
                if other_bag not in visited:
                    child_node = RootedTree.build_subtree(tree, other_bag, visited)
                    node.add_child(child_node)
        return node

class NiceTree(RootedTree):
    def __init__(self, root:Node, nodes):
        super().__init__(root, nodes)

if __name__ == "__main__":
    node1 = Node("0", [])
    node2 = Node("1", [])
    node3 = Node("0", [])
    node4 = Node("or", [node1, node2])
    node5 = Node("1", [])
    node6 = Node("not", [node3])
    node7 = Node("not", [node4])
    node8 = Node("or", [node5, node6])
    node9 = Node("and", [node7, node8])

    print(RootedTree(node9, [node1, node2, node3, node4, node5, node6, node7, node8, node9]))
    
