# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: thread_priorityQ.py
@time: 2020-01-23 13:27:15
@projectExplain: 
"""

import heapq
import threading


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._count = 0
        self._cv = threading.Condition()
    def put(self, item, priority):
        with self._cv:
            heapq.heappush(self._queue, (-priority, self._count, item))
            self._count += 1
            self._cv.notify()

    def get(self):
        with self._cv:
            while len(self._queue) == 0:
                self._cv.wait()
            return heapq.heappop(self._queue)[-1]