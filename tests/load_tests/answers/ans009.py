x = int(input())

if x < 0:
    print("false")
    exit()

original = x
reversed_num = 0

while x > 0:
    digit = x % 10
    reversed_num = reversed_num * 10 + digit
    x = x // 10

print("true" if original == reversed_num else "false")