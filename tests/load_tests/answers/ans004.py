m, *nums1 = map(int, input().split())
n, *nums2 = map(int, input().split())

A, B = nums1, nums2
if len(A) > len(B):
    A, B = B, A

total = len(A) + len(B)
half = total // 2

left, right = 0, len(A) - 1
while True:
    i = (left + right) // 2
    j = half - i - 2
    
    Aleft = A[i] if i >= 0 else float('-inf')
    Aright = A[i+1] if (i+1) < len(A) else float('inf')
    Bleft = B[j] if j >= 0 else float('-inf')
    Bright = B[j+1] if (j+1) < len(B) else float('inf')
    
    if Aleft <= Bright and Bleft <= Aright:
        if total % 2:
            print(float(min(Aright, Bright)))
        else:
            print((max(Aleft, Bleft) + min(Aright, Bright)) / 2)
        break
    elif Aleft > Bright:
        right = i - 1
    else:
        left = i + 1