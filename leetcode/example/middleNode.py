# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: middleNode.py
@time: 2020-03-23 10:04:34
@projectExplain: 876. 链表的中间结点
给定一个带有头结点 head 的非空单链表，返回链表的中间结点。
如果有两个中间结点，则返回第二个中间结点。
"""

# Definition for singly-linked list.
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def middleNode(self, head: ListNode) -> ListNode:
        fast, slow = head
        while fast and fast.next:
            if fast == slow:
                break
            slow = slow.next
            fast = fast.next.next

        return slow

def run(nums):
    head = ListNode(nums[0])
    cur = head
    for i in range(1, len(nums)):
        cur.next = ListNode(nums[i])
        cur = cur.next
    return head


if __name__ == '__main__':
    nums = [1,2,3,4,5,6]
    head = run(nums)
    res = Solution().middleNode(head)
    print(res)

