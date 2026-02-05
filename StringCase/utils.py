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



if __name__ == "__main__":
    elems = list({"q0", "q1", "qf"})
    for subset in powerset(elems):
        print(subset)