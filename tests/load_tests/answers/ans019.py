class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

m, *list1 = map(int, input().split())
n, *list2 = map(int, input().split())

def create_list(elements):
    dummy = ListNode()
    current = dummy
    for val in elements:
        current.next = ListNode(val)
        current = current.next
    return dummy.next

l1 = create_list(list1)
l2 = create_list(list2)

dummy = ListNode()
current = dummy

while l1 and l2:
    if l1.val <= l2.val:
        current.next = l1
        l1 = l1.next
    else:
        current.next = l2
        l2 = l2.next
    current = current.next

current.next = l1 if l1 else l2

result = []
current = dummy.next
while current:
    result.append(str(current.val))
    current = current.next

print(' '.join(result) if result else "")