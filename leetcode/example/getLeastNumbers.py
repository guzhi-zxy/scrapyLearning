# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: getLeastNumbers.py
@time: 2020-03-20 10:43:27
@projectExplain: 输入整数数组 arr ，找出其中最小的 k 个数。例如，输入4、5、1、6、2、7、3、8这8个数字，则最小的4个数字是1、2、3、4。
"""

from typing import List


class Solution:
    def getLeastNumbers(self, arr: List[int], k: int) -> List[int]:
        # 简单的升序排序非常简单：只需调用 sorted() 函数即可。它会返回一个新的已排序列表。
        # 使用 list.sort() 方法，它会直接修改原列表（并返回 None 以避免混淆），通常来说它不如 sorted() 方便 ——— 但如果你不需要原列表，它会更有效率。
        arr.sort()
        return arr[:k]


if __name__ == '__main__':
    arr = [1, 3, 54, 7, 8, 4, 42, 5, 6, 10]
    k = 6
    res = Solution().getLeastNumbers(arr, k)
    print(res)
