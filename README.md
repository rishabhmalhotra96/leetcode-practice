# 🧠 LeetCode Practice — Company-wise + Topic-wise Tracker

> **Personal LeetCode repository** with company-wise grouping, topic discoverability,
> spaced-repetition revision tracking, and a one-command dashboard update.

## 📂 Repository Structure

```
leetcode-practice/
├── solutions/               # Every solution file lives here (single source of truth)
│   └── lc_XXXX_slug.py
├── company/                 # Auto-generated per-company index pages (no code duplication)
│   ├── amazon.md
│   ├── google.md
│   └── …
├── topics/                  # Auto-generated per-topic index pages
│   ├── array.md
│   ├── dynamic_programming.md
│   └── …
├── templates/
│   └── solution_template.py # Copy this when adding a new problem
├── tracker/
│   └── problems.json        # Machine-readable source of truth (auto-updated)
├── scripts/
│   └── update_tracker.py    # Scan solutions → rebuild tracker + README + indexes
├── .github/workflows/
│   └── update_tracker.yml   # GitHub Action: auto-run on push/PR
└── README.md                # This file (dashboard auto-updated between <!-- markers -->)
```

---

## 🚀 How to Add a New Problem

1. **Copy the template**
   ```bash
   cp templates/solution_template.py solutions/lc_XXXX_problem_slug.py
   ```
2. **Fill in the metadata header** (YAML-like block at the top of the file)  
   — id, title, url, difficulty, companies, topics, status, hint_level, etc.
3. **Write your solution** below the template stubs.
4. **Update the tracker locally** (optional but recommended before pushing):
   ```bash
   python scripts/update_tracker.py
   ```
   This rebuilds `tracker/problems.json`, `README.md`, `company/*.md`, and `topics/*.md`.
5. **Commit everything** — the GitHub Action will also run automatically on push.

---

## 🔍 Querying Without Updating Files

```bash
# All REVISIT problems
python scripts/update_tracker.py --query --status REVISIT

# All Medium Graph problems
python scripts/update_tracker.py --query --difficulty Medium --topic Graph

# All Amazon problems
python scripts/update_tracker.py --query --company Amazon

# Combine filters (AND logic)
python scripts/update_tracker.py --query --company Google --difficulty Hard
```

---

## 🏷️ Status & Hint Legend

| Symbol | Status |
|--------|--------|
| ⬜ | TODO |
| 🔄 | IN_PROGRESS |
| ✅ | SOLVED |
| 🔁 | REVISIT |

| Symbol | Hint Level |
|--------|-----------|
| 💡 | NONE — solved independently |
| 🕯️ | LIGHT — needed a small nudge |
| 🆘 | HEAVY — needed significant help |

---

## 📊 Overall Stats

<!-- AUTO-GENERATED: STATS -->
> Last updated: **2026-04-18**

| Metric | Count |
|--------|-------|
| Total problems | 1 |
| ✅ Solved | 1 |
| 🔁 Revisit | 0 |
| 🔄 In Progress | 0 |
| ⬜ TODO | 0 |
| 🟢 Easy | 1 |
| 🟡 Medium | 0 |
| 🔴 Hard | 0 |
<!-- /AUTO-GENERATED: STATS -->

---

## 📋 All Problems

<!-- AUTO-GENERATED: ALL_PROBLEMS -->
| # | Title | Difficulty | Topics | Companies | Status | Hint | Confidence | File |
|---|-------|------------|--------|-----------|--------|------|------------|------|
| 121 | [121. Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | 🟢 Easy | Array, Dynamic Programming, Sliding Window | Amazon, Google, Microsoft, Facebook, Apple | ✅ SOLVED | 💡 NONE | ⭐⭐⭐⭐⭐ | [lc_0121_best_time_to_buy_and_sell_stock.py](solutions/lc_0121_best_time_to_buy_and_sell_stock.py) |
<!-- /AUTO-GENERATED: ALL_PROBLEMS -->

---

## 🔁 Revisit Queue

<!-- AUTO-GENERATED: REVISIT_QUEUE -->
_No problems in revisit queue right now. 🎉_
<!-- /AUTO-GENERATED: REVISIT_QUEUE -->

---

## 🗂️ By Topic

<!-- AUTO-GENERATED: TOPIC_BREAKDOWN -->
| Topic | Total | Solved | Revisit | TODO |
|-------|-------|--------|---------|------|
| Array | 1 | 1 | 0 | 0 |
| Dynamic Programming | 1 | 1 | 0 | 0 |
| Sliding Window | 1 | 1 | 0 | 0 |
<!-- /AUTO-GENERATED: TOPIC_BREAKDOWN -->

> Full per-topic problem lists: see [topics/](topics/)

---

## 🏢 By Company

<!-- AUTO-GENERATED: COMPANY_BREAKDOWN -->
| Company | Total | Solved | Revisit | TODO |
|---------|-------|--------|---------|------|
| Amazon | 1 | 1 | 0 | 0 |
| Apple | 1 | 1 | 0 | 0 |
| Facebook | 1 | 1 | 0 | 0 |
| Google | 1 | 1 | 0 | 0 |
| Microsoft | 1 | 1 | 0 | 0 |
<!-- /AUTO-GENERATED: COMPANY_BREAKDOWN -->

> Full per-company problem lists: see [company/](company/)
