class Solution(object):
    def twoSum(self, numbers, target):
        """
        :type numbers: List[int]
        :type target: int
        :rtype: List[int]
        """
        i = 0
        j = len(numbers) - 1

        while i < j:
            l = numbers[i]
            r = numbers[j]
            t = l + r
            if t == target:
                return [i + 1, j + 1]
            elif t < target:
                i += 1
            elif t > target:
                j -= 1
