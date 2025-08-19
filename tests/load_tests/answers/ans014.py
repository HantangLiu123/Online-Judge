n = int(input())
strs = [input().strip() for _ in range(n)]

if not strs:
    print("")
    exit()

prefix = strs[0]
for s in strs[1:]:
    while s[:len(prefix)] != prefix:
        prefix = prefix[:-1]
        if not prefix:
            print("")
            exit()

print(prefix)