class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        h = {}

        for j in range(len(nums)):
            i = nums[j]
            c = target - i
            if i in h:
                return [h[i], j]
            h[c] = j
