
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