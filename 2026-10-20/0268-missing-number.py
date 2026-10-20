class Solution(object):
    def missingNumber(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        s = (range(len(nums)+1))
        result = 0
        #print(s)
        l = len(nums)
        for i in s:
            if i < l:
                result ^= (i ^ nums[i])
            else:
                result ^= i
        return result
