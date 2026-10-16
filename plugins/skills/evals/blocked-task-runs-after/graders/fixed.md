---
type: llm
focus: { source: file, path: src/dates.py }
---
PASS if src/dates.py returns a non-negative day count (for example abs((a - b).days)).
FAIL if days_between can still return a negative number.
