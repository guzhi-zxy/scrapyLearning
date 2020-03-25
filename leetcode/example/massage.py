# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: massage.py
@time: 2020-03-24 09:51:32
@projectExplain: 面试题 17.16. 按摩师
一个有名的按摩师会收到源源不断的预约请求，每个预约都可以选择接或不接。在每次预约服务之间要有休息时间，因此她不能接受相邻的预约。给定一个预约请求序列，替按摩师找到最优的预约集合（总预约时间最长），返回总的分钟数。
"""
from typing import List


class Solution:
    def massage(self, nums: List[int]) -> int:
        if not nums: return 0
        last, now = 0, nums[0]
        for index in range(1, len(nums)):
            last, now = max(last, now), last + nums[index]

        return max(last, now)


if __name__ == '__main__':
    nums = [2, 1, 4, 5, 3, 1, 1, 3]
    res = Solution().massage(nums)
    print(res)
