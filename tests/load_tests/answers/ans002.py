class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

n = int(input())
l1_digits = list(map(int, input().split()))
m = int(input())
l2_digits = list(map(int, input().split()))

# Helper function to create linked list
def create_list(digits):
    if not digits:
        return None
    head = ListNode(digits[0])
    current = head
    for digit in digits[1:]:
        current.next = ListNode(digit)
        current = current.next
    return head

l1 = create_list(l1_digits)
l2 = create_list(l2_digits)

dummy = ListNode()
current = dummy
carry = 0

while l1 or l2 or carry:
    sum_val = carry
    if l1:
        sum_val += l1.val
        l1 = l1.next
    if l2:
        sum_val += l2.val
        l2 = l2.next
    
    carry = sum_val // 10
    current.next = ListNode(sum_val % 10)
    current = current.next

result = []
current = dummy.next
while current:
    result.append(str(current.val))
    current = current.next

print(' '.join(result))