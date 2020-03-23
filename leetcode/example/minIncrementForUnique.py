# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: minIncrementForUnique.py
@time: 2020-03-22 00:21:59
@projectExplain: 945. 使数组唯一的最小增量
给定整数数组 A，每次 move 操作将会选择任意 A[i]，并将其递增 1。
返回使 A 中的每个值都是唯一的最少操作次数。
"""
from typing import List


class Solution:
    def minIncrementForUnique(self, A: List[int]) -> int:
        # 贪心算法
        if not A: return 0
        A.sort()
        cnt = 0
        for element in range(1, len(A)):
            if A[element] <= A[element - 1]:
                cnt += A[element - 1] - A[element] + 1
                A[element] = A[element - 1] + 1
        return cnt


if __name__ == '__main__':
    A = [3, 2, 1, 2, 1, 7]
    res = Solution().minIncrementForUnique(A)
    print(res)
