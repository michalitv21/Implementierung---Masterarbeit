from treeAutomata import TreeAutomaton
from treeDecomp import Node, RootedTree


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

t1 = RootedTree(t1n11, [t1n1, t1n2, t1n3, t1n4, t1n5, t1n6, t1n7, t1n8, t1n9, t1n10, t1n11])

# Automaton that accepts trees with even number of 'a' leaves
even_a = TreeAutomaton(
    states={"q_even", "q_odd"},
    input_symbols={
        "a":2, "b":2, "leaf":0},  
    final_states={"q_even"},
    transitions={
        "leaf" : ["q_even"],

        
            "a": 
            {"q_even": 
                {"q_even": ["q_odd"], "q_odd": ["q_even"]}, #left child state
             "q_odd": 
                {"q_even": ["q_even"], "q_odd": ["q_odd"]}
            }, #right child state
        

        
            "b": 
            {"q_even": 
                {"q_even": ["q_even"], "q_odd": ["q_odd"]}, #left child state
             "q_odd": 
                {"q_even": ["q_odd"], "q_odd": ["q_even"]}}, #right child state
        
    }
)

# Automaton that accepts trees with even number of 'b' leaves
even_b = TreeAutomaton(
    states={"q_even", "q_odd"},
    input_symbols={
        "a":2, "b":2, "leaf":0},  
    final_states={"q_even"},
    transitions={
        "leaf": ["q_even"],

        
            "a":
            {"q_even": 
                {"q_even": ["q_even"], "q_odd": ["q_odd"]}, #left child state
             "q_odd": 
                {"q_even": ["q_odd"], "q_odd": ["q_even"]}
            }, #right child state
        

        
            "b":
            {"q_even": 
                {"q_even": ["q_odd"], "q_odd": ["q_even"]}, #left child state - flips parity
             "q_odd": 
                {"q_even": ["q_even"], "q_odd": ["q_odd"]}}, #right child state - flips parity
        
    }    
)

result_states_a = even_a.run(t1)
print("even_a:", result_states_a)

result_states_b = even_b.run(t1)
print("even_b:", result_states_b)

result_states_a_complement = even_a.complement().run(t1)
print("complement of even_a:", result_states_a_complement)

result_states_b_complement = even_b.complement().run(t1)
print("complement of even_b:", result_states_b_complement)

result_states_union = even_a.union(even_b).run(t1)
print("union of even_a and even_b:", result_states_union) 

result_states_union_odd_a_even_b = even_a.complement().union(even_b).run(t1)
print("union of odd_a and even_b:", result_states_union_odd_a_even_b)

result_states_union_even_a_odd_b = even_a.union(even_b.complement()).run(t1)
print("union of even_a and odd_b:", result_states_union_even_a_odd_b)

result_states_cut = even_a.cut(even_b).run(t1)
print("cut of even_a and even_b:", result_states_cut)

result_states_cut_odd_a_even_b = even_a.complement().cut(even_b).run(t1)
print("cut of odd_a and even_b:", result_states_cut_odd_a_even_b)