x = int(input())

sign = -1 if x < 0 else 1
x = abs(x)
rev = 0

while x != 0:
    pop = x % 10
    x = x // 10
    rev = rev * 10 + pop

rev *= sign

if rev < -2**31 or rev > 2**31 - 1:
    print(0)
else:
    print(rev)