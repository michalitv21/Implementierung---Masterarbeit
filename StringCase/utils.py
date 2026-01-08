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


if __name__ == "__main__":
    elems = list({"q0", "q1", "qf"})
    for subset in powerset(elems):
        print(subset)
        


    