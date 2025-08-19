s = input().strip()

stack = []
mapping = {')': '(', '}': '{', ']': '['}

for char in s:
    if char in mapping:
        top = stack.pop() if stack else '#'
        if mapping[char] != top:
            print("false")
            exit()
    else:
        stack.append(char)

print("true" if not stack else "false")