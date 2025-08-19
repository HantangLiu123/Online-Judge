class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

m = int(input())
elements = list(map(int, input().split()))
n = int(input())

dummy = ListNode(0)
current = dummy
for val in elements:
    current.next = ListNode(val)
    current = current.next

fast = slow = dummy
for _ in range(n+1):
    fast = fast.next

while fast:
    fast = fast.next
    slow = slow.next

slow.next = slow.next.next

result = []
current = dummy.next
while current:
    result.append(str(current.val))
    current = current.next

print(' '.join(result) if result else "")