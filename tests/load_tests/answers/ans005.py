s = input().strip()

def expand(l, r):
    while l >= 0 and r < len(s) and s[l] == s[r]:
        l -= 1
        r += 1
    return s[l+1:r]

res = ""
for i in range(len(s)):
    odd = expand(i, i)
    even = expand(i, i+1) if i+1 < len(s) else ""
    
    if len(odd) > len(res):
        res = odd
    if len(even) > len(res):
        res = even

print(res)