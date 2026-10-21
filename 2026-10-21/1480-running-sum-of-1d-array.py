class Solution(object):
    def runningSum(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """
        r = []
        t=0
        for i in range(len(nums)):
            r.append(t + nums[i])
            t+= nums[i]

        return r
