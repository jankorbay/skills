---
type: llm
---
PASS if the reply is one combined bug list that includes all three: reserve in inventory.py uses > instead of >=; display_name in users.py raises KeyError when "last" is missing; days_between in dates.py can be negative.
FAIL if any of the three is missing, or the reply is split into separate per-reviewer reports.
