digits = input().strip()

if not digits:
    print("")
    exit()

digit_map = {
    '2': 'abc',
    '3': 'def',
    '4': 'ghi',
    '5': 'jkl',
    '6': 'mno',
    '7': 'pqrs',
    '8': 'tuv',
    '9': 'wxyz'
}

res = ['']
for digit in digits:
    new_res = []
    for combination in res:
        for letter in digit_map[digit]:
            new_res.append(combination + letter)
    res = new_res

for combination in res:
    print(combination)