
class Bag:
    def __init__(self, label:str, vertices:set):
        self.label = label
        self.vertices = vertices
        
        
    def add_vertex(self, v):
        self.vertices.append(v)

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