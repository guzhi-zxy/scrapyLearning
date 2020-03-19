# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: priorityQ.py
@time: 2020-01-23 13:14:23
@projectExplain: 
"""

import heapq


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        print('==', self._queue)
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]


class Item:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Item({!r})".format(self.name)



if __name__ == '__main__':
    q = PriorityQueue()
    q.push(Item('foo'),1)
    q.push(Item('qoo'), 4)
    q.push(Item('koo'), 2)
    print(q.pop())
    print(q.pop())
    print(q.pop())


