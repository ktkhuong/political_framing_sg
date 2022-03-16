import re
import difflib

# longest common substrings (https://www.bogotobogo.com/python/python_longest_common_substring_lcs_algorithm_generalized_suffix_tree.php) 
def lcs(S, T):
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i-c+1:i+1])
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])

    return lcs_set

def main():
    with open("parliament\\mp.txt", "r") as f:
        names = [re.sub(r"[^a-z.]", "", line.replace("\n","").lower().strip()) for line in f.readlines() if line.strip()]
        names = "".join(names)
    print(lcs(names, "the minister for law and national development mr e w barker"))

if __name__ == "__main__":
    main()