# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: kthSmallest.py
@time: 2020-03-21 20:58:40
@projectExplain: 378. 有序矩阵中第K小的元素
给定一个 n x n 矩阵，其中每行和每列元素均按升序排序，找到矩阵中第k小的元素。
请注意，它是排序后的第k小元素，而不是第k个元素。
"""

import heapq
from typing import List


class Solution:
    def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
        return sorted([element for lst in matrix for element in lst])[k - 1]


class Solution2:
    def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
        return heapq.nsmallest(k, [element for lst in matrix for element in lst])[-1]


if __name__ == '__main__':
    matrix = [
        [1, 5, 9],
        [10, 11, 13],
        [12, 13, 15]
    ]
    k = 8
    res = Solution2().kthSmallest(matrix, k)
    print(res)
