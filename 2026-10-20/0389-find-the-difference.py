class Solution(object):
    def findTheDifference(self, s, t):
        """
        :type s: str
        :type t: str
        :rtype: str
        """
        result = 0
        l = len(s)
        for i in range(l+1):
            if i < l:
                result ^= (ord(s[i]) ^ ord(t[i]))
            else:
                result ^= ord(t[i])
        
        
        return(chr(result))
