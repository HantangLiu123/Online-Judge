s = input().strip()
numRows = int(input())

if numRows == 1:
    print(s)
    exit()

rows = [[] for _ in range(numRows)]
direction = -1
current_row = 0

for char in s:
    rows[current_row].append(char)
    if current_row == 0 or current_row == numRows - 1:
        direction *= -1
    current_row += direction

result = []
for row in rows:
    result.extend(row)
print(''.join(result))