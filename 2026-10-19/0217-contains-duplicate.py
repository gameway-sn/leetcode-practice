from collections import Counter
class Solution(object):
    def containsDuplicate(self, nums):
        """
        :type nums: List[int]
        :rtype: bool
        """
        t = Counter(nums)

        for key, value in t.items():
            if value > 1:
                return True

        return False
