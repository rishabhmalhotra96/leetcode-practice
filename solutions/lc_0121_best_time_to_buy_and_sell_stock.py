# ---
# id: 121
# title: "Best Time to Buy and Sell Stock"
# url: "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"
# difficulty: Easy
# companies: [Amazon, Google, Microsoft, Facebook, Apple]
# topics: [Array, Dynamic Programming, Sliding Window]
# status: SOLVED
# hint_level: NONE
# time_complexity: O(n)
# space_complexity: O(1)
# key_insight: |
#   Track the minimum price seen so far (buy candidate).
#   At each step compute profit = current - min_price and update max_profit.
#   Single left-to-right pass; no nested loops needed.
# pitfalls: "Don't reset min_price after computing profit – keep the global min."
# last_reviewed: 2026-04-18
# next_review: 2026-04-25
# confidence: 5
# ---

# ─── PATTERN ──────────────────────────────────────────────────────────────────
# Greedy / Single-pass min tracking
#
# ─── KEY IDEA ─────────────────────────────────────────────────────────────────
# We want max(prices[j] - prices[i]) for j > i.
# Sweep left→right: keep a running minimum (cheapest buy day seen so far) and
# at each price update the best profit.  Never need to look back.
#
# ─── COMPLEXITY ───────────────────────────────────────────────────────────────
# Time:  O(n)   Space: O(1)
# ──────────────────────────────────────────────────────────────────────────────

from typing import List


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        min_price = float("inf")
        max_profit = 0

        for price in prices:
            if price < min_price:
                min_price = price          # found a cheaper buy day
            elif price - min_price > max_profit:
                max_profit = price - min_price  # found a better profit

        return max_profit


# ─── TEST CASES ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    s = Solution()
    assert s.maxProfit([7, 1, 5, 3, 6, 4]) == 5,  "Expected 5"
    assert s.maxProfit([7, 6, 4, 3, 1]) == 0,      "Expected 0 (no profit)"
    assert s.maxProfit([1]) == 0,                   "Expected 0 (single price)"
    assert s.maxProfit([2, 4, 1]) == 2,             "Expected 2"
    print("All tests passed.")
