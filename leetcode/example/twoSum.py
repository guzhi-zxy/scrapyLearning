# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: twoSum.py
@time: 2020-03-22 23:52:33
@projectExplain: 1. 两数之和
给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那 两个 整数，并返回他们的数组下标。
你可以假设每种输入只会对应一个答案。但是，你不能重复利用这个数组中同样的元素。
"""
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        redict = {}
        for index, num in enumerate(nums):
            if target - num in redict:
                return [redict[target - num], index]
            redict[num] = index

if __name__ == '__main__':
    nums = [3,2,4]
    target = 6
    res = Solution().twoSum(nums, target)
    print(res)
