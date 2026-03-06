symbols = ["a", "b", "c", "d", "e", "f", "g"]

def powerset(elems):
    powerset_size = 2**len(elems)
    counter = 0
    j = 0
 
    for counter in range(0, powerset_size):
        results = []
        for j in range(0, len(elems)):
            # take the element if on bit position j it says to take it (i.e. 1 appears)
            if((counter & (1 << j)) > 0):
                results.append(elems[j])
        yield results

        

def gen_new_alphabet(alphabet, k):
    """
    Docstring for gen_new_alphabet
    
    :param alphabet: Symbols that are used
    :param k: Depth of Quantors

    Example: gen_new_alphabet({'a','b'}, 2) -> {('a',0,0), ('a',0,1), ('a',1,0), ('a',1,1), ('b',0,0), ('b',0,1), ('b',1,0), ('b',1,1)}
    """
    
    new_alphabet = set()
    for symbol in alphabet:
        def generate_tuples(current_tuple, depth):
            if depth == k:
                new_alphabet.add((symbol,) + current_tuple)
                return
            for i in range(2):
                generate_tuples(current_tuple + (i,), depth + 1)
        generate_tuples((), 0)
    return new_alphabet

"""
Works for treewidth up to 6, k is number of quantors
Alphabet will be of form ({a, b, c, d, e, f, g} x {a, b, c, d, e, f, g}) x ({0, 1} x {0, 1})^k + "//" + ren_ and miv_ for every symbol
Leafs represent the edge introductions and have arity 0
Every symbol needs to have every 2-bit combination for each of the k quantors, i.e. for k=2
and symbol ab we need ("ab", "00", "01"), ("ab", "10", "11"), ... in the alphabet 
In the end "//" is added with arity 2 and ren_ and miv_ for every symbol with arity 1
"""
def gen_courcelle_alphabet(tree_width, k):
    new_alphabet = []
    sym_k = symbols[:tree_width+1]
    for s1 in sym_k:
        for s2 in sym_k:
            if s1 == s2:
                continue
            pair = s1 + s2
            def generate_tuples(current_tuple, depth, sym=pair):
                if depth == k:
                    new_alphabet.append((sym,) + current_tuple)
                    return
                for bits in ["00", "01", "10", "11"]:
                    generate_tuples(current_tuple + (bits,), depth + 1, sym)
            generate_tuples((), 0)
    ranked_alphabet = {sym: 0 for sym in new_alphabet}
    ranked_alphabet["//"] = 2
    functional_symbols = {f"ren_{s1}{s2}": 1 for s1 in sym_k for s2 in sym_k if s1 != s2} | {f"miv_{x}": 1 for x in sym_k}
    ranked_alphabet.update(functional_symbols)
    return ranked_alphabet

if __name__ == "__main__":
    print(gen_courcelle_alphabet(2, 2))


