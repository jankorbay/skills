---
description: A task that needs another task's result starts only after it, with that result in its brief.
runs: 3
model: opus
max_turns: 40
timeout_seconds: 900
---
/skills:delegator Two steps. Step 1: research whether days_between in src/dates.py should return an absolute number of days, based on its name and how it could be used. Step 2: based on that conclusion, fix days_between and add a test for it in tests/test_dates.py.
