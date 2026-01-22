import re
from mso import MSO_Parser

alphabet = {'a', 'b', 'c', 'd'}

def count_quantified_vars(formula):
    """Count the number of quantified variables in a formula"""
    quantifiers = re.findall(r'[∃∀E]', formula)
    return len(quantifiers)

test_formulas = [
    # === FIRST-ORDER ONLY (baseline) ===
    # 1. There exists an 'a'
    (
        "∃x(P_a(x))",
        ["a", "ba", "ca", "aaa", "bab"],
        ["b", "c", "bc", ""]
    ),
    
    # 2. There exist 'a' and 'b' in word
    (
        "∃x(∃y(and(P_a(x), P_b(y))))",
        ["ab", "ba", "aab", "abb", "bab"],
        ["a", "b", "c", "aa", "bb", ""]
    ),
    
    # 3. There exists 'a' followed by 'b' (a before or at same position as b)
    (
        "∃x(∃y(and(and(P_a(x), P_b(y)), le(x,y))))",
        ["ab", "aab", "abb", "ba", "cab"],
        ["b", "a", "c"]
    ),
    
    # === SINGLE SET (second-order) ===
    # 4. Set X marks at least one 'a' position
    (
        "∃X(∃x(and(P_a(x), in(X,x))))",
        ["a", "ba", "ca", "aab"],
        ["b", "c", "bc", ""]
    ),
    
    # 5. Set X marks all 'a' positions (and only 'a' positions)
    (
        "∃X(and(∀x(or(not(P_a(x)), in(X,x))), ∀y(or(not(in(X,y)), P_a(y)))))",
        ["a", "aa", "ba", "cab", ""],
        ["ab", "ac", "aba"]
    ),
    
    # 6. Set X marks all 'b' positions
    (
        "∃X(and(∀x(or(not(P_b(x)), in(X,x))), ∀y(or(not(in(X,y)), P_b(y)))))",
        ["b", "bb", "ab", "cab", ""],
        ["a", "bc", "bab"]
    ),
    
    # === TWO SETS ===
    # 7. Set X marks 'a' positions, Set Y marks 'b' positions
    (
        "∃X(∃Y(and(and(∀x(or(not(P_a(x)), in(X,x))), ∀y(or(not(in(X,y)), P_a(y)))), and(∀u(or(not(P_b(u)), in(Y,u))), ∀v(or(not(in(Y,v)), P_b(v))))))",
        ["ab", "ba", "aabb", "abab", ""],
        ["c", "abc", "aca"]
    ),
    
    # 8. Both sets X and Y are nonempty
    (
        "∃X(∃Y(and(∃x(in(X,x)), ∃y(in(Y,y)))))",
        ["a", "ab", "abc", "aabbcc"],
        [""]
    ),
    
    # 9. Set X and Y partition positions (each position in at least one)
    (
        "∃X(∃Y(∀x(or(in(X,x), in(Y,x)))))",
        ["a", "ab", "abc", "abcd"],
        [""]
    ),
    
    # === THREE SETS ===
    # 10. Sets X, Y, Z mark 'a', 'b', 'c' positions respectively
    (
        "∃X(∃Y(∃Z(and(and(and(∀x(or(not(P_a(x)), in(X,x))), ∀x(or(not(in(X,x)), P_a(x)))), and(∀y(or(not(P_b(y)), in(Y,y))), ∀y(or(not(in(Y,y)), P_b(y))))), and(∀z(or(not(P_c(z)), in(Z,z))), ∀z(or(not(in(Z,z)), P_c(z)))))))",
        ["abc", "cab", "bca", "aabbcc", ""],
        ["ad", "abcd", "abac"]
    ),
    
    # === MIXED FIRST & SECOND ORDER ===
    # 11. Position x is in set X and marks 'a'
    (
        "∃X(∃x(and(and(in(X,x), P_a(x)), ∀y(or(not(in(X,y)), P_a(y))))))",
        ["a", "aa", "ba", "cab"],
        ["b", "c", "ab"]
    ),
    
    # 12. There's a position x and sets that partition around x
    (
        "∃X(∃Y(∃x(and(and(in(X,x), ∀p(or(not(le(p,x)), in(X,p)))), ∀q(or(not(le(x,q)), in(Y,q)))))))",
        ["a", "ab", "abc"],
        []
    ),
    
    # === MORE COMPLEX (careful with negations) ===
    # 13. Set X is nonempty and marked positions have only 'a' and 'b'
    (
        "∃X(and(∃x(in(X,x)), ∀y(or(not(in(X,y)), or(P_a(y), P_b(y))))))",
        ["a", "ab", "ba", "aabb"],
        ["c", "abc", "ac"]
    ),
    
    # 14. Sets X marks 'a' positions, Y marks 'b' positions, and they're disjoint
    (
        "∃X(∃Y(and(and(∀x(or(not(P_a(x)), in(X,x))), ∀x(or(not(in(X,x)), P_a(x)))), and(and(∀y(or(not(P_b(y)), in(Y,y))), ∀y(or(not(in(Y,y)), P_b(y)))), ∀z(or(or(not(in(X,z)), not(in(Y,z)))))))",
        ["ab", "ba", "aabb", "abab"],
        ["", "aa", "bb"]
    ),
    
    # 15. Position x marks 'a', and set X marks all 'a' positions after x
    (
        "∃X(∃x(and(P_a(x), ∀y(or(or(not(P_a(y)), not(le(x,y))), in(X,y))))))",
        ["a", "aa", "ba", "aab"],
        ["b", ""]
    ),
]

for i, (formula, should_accept, should_reject) in enumerate(test_formulas, 1):
    k = count_quantified_vars(formula)
    print(f"\n{'='*90}")
    print(f"Test {i:2d} (k={k})")
    print(f"{'='*90}")
    print(f"{formula}")
    print()
    
    parser = MSO_Parser(alphabet, k)
    try:
        ast = parser.build_ast(formula)
        parser.k = k  # Reset k to original value
        automaton = parser.build_automaton(ast)
        
        print("  ✓ Accept:")
        correct = 0
        for word in should_accept:
            result = automaton.nfa_run(word)
            status = "✓" if result else "✗"
            if result:
                correct += 1
            print(f"    {status} '{word}' = {result}")
        print(f"    -> {correct}/{len(should_accept)} correct")
        
        print("  ✗ Reject:")
        correct = 0
        for word in should_reject:
            result = automaton.nfa_run(word)
            status = "✓" if not result else "✗"
            if not result:
                correct += 1
            print(f"    {status} '{word}' = {result}")
        print(f"    -> {correct}/{len(should_reject)} correct")
            
    except Exception as e:
        import traceback
        print(f"  ❌ ERROR: {e}")
        traceback.print_exc()

print("\n" + "="*90)
print("TESTING COMPLETE")
print("="*90)
