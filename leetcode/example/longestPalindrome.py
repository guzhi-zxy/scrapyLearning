# -*- coding: utf-8 -*-

"""
@author: guzhi
@file: longestPalindrome.py.py
@time: 2020-03-19 23:59:35
@projectExplain: 给定一个包含大写字母和小写字母的字符串，找到通过这些字母构造成的最长的回文串。

在构造过程中，请注意区分大小写。比如 "Aa" 不能当做一个回文字符串。

注意:
假设字符串的长度不会超过 1010。
"""

from collections import Counter


class Solution:
    def longestPalindrome(self, s: str) -> int:
        values = Counter(s).values()
        status = False
        length = 0
        for v in values:
            if v % 2:
                status = True
            length += 2 * (v // 2)
        if status:
            length += 1
        return length


if __name__ == '__main__':
    s = "abccccdd"
    res = Solution().longestPalindrome(s)
    print(res)
