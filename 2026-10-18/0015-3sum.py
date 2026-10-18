class Solution(object):
    def threeSum(self, nums):
        nums.sort()
        res = set()
        i = 0

        while i < len(nums) - 2:

            if i > 0 and nums[i] == nums[i - 1]:
                i += 1
                continue

            j = i + 1
            k = len(nums) - 1
            target = -nums[i]

            while j < k:
                s = nums[j] + nums[k]

                if s == target:
                    res.add((nums[i], nums[j], nums[k]))

                    j += 1
                    k -= 1

                    while j < k and nums[j] == nums[j - 1]:
                        j += 1

                    while j < k and nums[k] == nums[k + 1]:
                        k -= 1

                elif s < target:
                    j += 1
                else:
                    k -= 1

            i += 1

        return [list(x) for x in res]
