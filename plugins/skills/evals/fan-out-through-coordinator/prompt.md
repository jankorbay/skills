---
description: One goal split across several reviewers goes through a single coordinator at the delegator's model.
runs: 3
model: opus
max_turns: 30
timeout_seconds: 900
---
/skills:delegator Review src/pricing.py, src/dates.py, src/inventory.py and src/users.py for bugs. Use a separate reviewer for each file and give me one combined list, most severe first.
