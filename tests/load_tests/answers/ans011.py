n  = int(input())
height = [int(num) for num in input().split()]

left, right = 0, len(height) - 1
max_area = 0

while left < right:
    # Calculate current area
    width = right - left
    current_height = min(height[left], height[right])
    current_area = width * current_height
    max_area = max(max_area, current_area)
    
    # Move the pointer with smaller height
    if height[left] < height[right]:
        left += 1
    else:
        right -= 1

print(max_area)