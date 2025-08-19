n = int(input())
nums = list(map(int, input().split()))
target = int(input())

hash_map = {}
for i, num in enumerate(nums):
    complement = target - num
    if complement in hash_map:
        print(hash_map[complement], i)
        exit()
    hash_map[num] = i