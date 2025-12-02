from treeDecomp import Bag, Tree

class Vertex:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label
    
    def __repr__(self):
        return self.label

class Graph:
    def __init__(self, vertices:list, edges:list):
        self.vertices = vertices
        self.edges = edges

    def adj(self, v1, v2):
        return set([v1,v2]) in self.edges
    
    def get_adj_verts(self, v:Vertex):
        res = []
        for e in self.edges:
            if v in e:
                for x in e:
                    res.append(x)
        res = set(res)
        if v in res:
            res.remove(v)
        return res

    def get_degree(self, v:Vertex):
        return len(self.get_adj_verts(v))

    def get_degree_dict(self):
        res = {}
        for v in self.vertices:
            res[v] = self.get_degree(v)
        return res

    def add_fill_in_edges(self, v:Vertex):
        adjecent_verts = self.get_adj_verts(v)
        for u in self.vertices:
            if u not in adjecent_verts:
                for w in self.vertices:
                    if w not in adjecent_verts:
                        self.edges.append(set([u,w]))

    def remove_vertex(self, v:Vertex):
        for e in self.edges.copy():
            #print("checking: " + str(e))
            if v in e:
                #print("removing :" + str(e))
                self.edges.remove(e)
        self.vertices.remove(v)

    def eliminate_vertex(self, v:Vertex):
        h = self.remove_vertex(v)
        h = self.add_fill_in_edges(v)
        return h

    def make_neighborhood_clique(self, v:Vertex):
        adjecent_verts = self.get_adj_verts(v)
        for u in adjecent_verts:
            for w in adjecent_verts:
                if u != w and {u, w} not in self.edges:
                    self.edges.append(set([u,w]))

def minimal_degree_ordering(g):
    ordering = []
    #print("g Vertices: " + str(g.vertices))
    h = Graph(g.vertices.copy(), g.edges.copy())
    for i in range(1,len(h.vertices)):
        degrees = h.get_degree_dict()
        min_deg_vert = min(degrees, key=degrees.get)
        #print("Min degree: " + min_deg_vert.label)
        ordering.append(min_deg_vert)
        #h.add_fill_in_edges(min_deg_vert)
        h.make_neighborhood_clique(min_deg_vert)
        h.remove_vertex(min_deg_vert) 
    return ordering

    
def createBags(graph:Graph, vertexList, bags):
    if (len(vertexList) == 1):
        bags[vertexList[0]] = Bag(vertexList[0].label, [vertexList[0]])
        return bags
    next_vert = vertexList[0]
    #print("Vertex 0: " + str(vertexList[0].label))
    #print(vertexList)
    #print(vertexList[0])
    bag = Bag(next_vert.label, [next_vert])
    for n in graph.get_adj_verts(next_vert):
        bag.add_vertex(n)
    bags[next_vert] = bag
    #print([x.vertices for x in bags])
    #print(graph_copy.vertices)
    
    graph.make_neighborhood_clique(next_vert)
    graph.remove_vertex(next_vert)
    
    #print("V after rem: " + str(graph.vertices))
    #print("E after rem: " + str(graph.edges))
    return createBags(graph, vertexList[1:], bags)

def permutationToTreeDecomposition(graph:Graph, vertexList):
    vertexList_copy = vertexList.copy()
    bags = createBags(graph, vertexList_copy, {})
    
    resTree = Tree(bags, [])
    for i in range(len(vertexList)):
        for j in range(i+1, len(vertexList)):
            if vertexList[j] in bags[vertexList[i]].vertices:
                resTree.add_edge(bags[vertexList[i]], bags[vertexList[j]])
                break
    return resTree

if __name__ == "__main__":
    a = Vertex("a")
    b = Vertex("b")
    c = Vertex("c")
    d = Vertex("d")
    e = Vertex("e")
    f = Vertex("f")
    g = Vertex("g")
    h = Vertex("h")

    #Paper1
    graph = Graph([a,b,c,d,e,f,g,h],[{a,b},{a,d},{a,e},{b,c},{b,f},{d,e},{e,f},{e,g},{e,h},{g,h}])
    graph_copy = Graph(graph.vertices.copy(), graph.edges.copy())

    #Paper2
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
    #print("a and b adjacent? : " + str(graph.adj(a,b)))
    #print("a and h adjacent? : " + str(graph.adj(a,h)))
    #print("Neighbours of a: " + str([x.label for x in graph.get_adj_verts(a)]))
    #print("Neighbours of e: " + str([x.label for x in graph.get_adj_verts(e)]))
    #for v in graph.vertices:
    #    print("#Neigbours of " + v.label + " : " + str(graph.get_degree(v)))
    #print(graph2.get_degree_dict())
    #print([x.label for x in graph.mininal_degree_ordering()])
    #print(graph.vertices)
    #print([x.label for x in minimal_degree_ordering(graph2)])
    #print(permutationToTreeDecomposition(graph2, minimal_degree_ordering(graph2), []))
    #print(graph2_copy.edges)
    print(permutationToTreeDecomposition(graph2_copy, [v10, v9, v8, v7, v2, v3, v6, v1, v5, v4]))