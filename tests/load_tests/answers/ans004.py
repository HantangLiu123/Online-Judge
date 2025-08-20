def findMedianSortedArrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    total = m + n
    half = total // 2
    
    left, right = 0, m
    
    while left <= right:
        i = (left + right) // 2
        j = half - i
        
        left1 = nums1[i-1] if i > 0 else float('-inf')
        right1 = nums1[i] if i < m else float('inf')
        left2 = nums2[j-1] if j > 0 else float('-inf')
        right2 = nums2[j] if j < n else float('inf')
        
        if left1 <= right2 and left2 <= right1:
            if total % 2 == 1:
                return float(min(right1, right2))
            else:
                return (max(left1, left2) + min(right1, right2)) / 2.0
        elif left1 > right2:
            right = i - 1
        else:
            left = i + 1

m = int(input().strip())
if m > 0:
    nums1 = list(map(int, input().split()))
else:
    input()
    nums1 = []

n = int(input().strip())
if n > 0:
    nums2 = list(map(int, input().split()))
else:
    input()
    nums2 = []

result = findMedianSortedArrays(nums1, nums2)
print(result)