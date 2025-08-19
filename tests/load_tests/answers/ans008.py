s = input().strip()

i = 0
n = len(s)
sign = 1
result = 0

# Skip whitespace
while i < n and s[i] == ' ':
    i += 1

# Handle sign
if i < n and (s[i] == '+' or s[i] == '-'):
    sign = -1 if s[i] == '-' else 1
    i += 1

# Process digits
while i < n and s[i].isdigit():
    digit = int(s[i])
    # Check for overflow
    if result > (2**31 - 1 - digit) // 10:
        print(-2**31 if sign == -1 else 2**31 - 1)
        exit()
    result = result * 10 + digit
    i += 1

print(sign * result)