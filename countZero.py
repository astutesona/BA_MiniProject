class Solution:
    def countServers(self, n: int, logs: List[List[int]], x: int, queries: List[int]) -> List[int]:
        logs.sort(key=lambda log: log[1])
        order = sorted(range(len(queries)), key=lambda i: queries[i])

        cnt = [0] * (n + 1)
        active = 0
        l = r = 0
        m = len(logs)
        ans = [0] * len(queries)

        for i in order:
            q = queries[i]

            # add logs with time <= q
            while r < m and logs[r][1] <= q:
                s = logs[r][0]
                if cnt[s] == 0:
                    active += 1
                cnt[s] += 1
                r += 1

            # remove logs with time < q - x
            while l < r and logs[l][1] < q - x:
                s = logs[l][0]
                cnt[s] -= 1
                if cnt[s] == 0:
                    active -= 1
                l += 1

            ans[i] = n - active

        return ans
