class Solution(object):
    def findDuplicates(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """
        s = set()
        res = []

        for i in nums:
            if i in s:
                res.append(i)
                s.remove(i)
                continue
            s.add(i)

        return res
