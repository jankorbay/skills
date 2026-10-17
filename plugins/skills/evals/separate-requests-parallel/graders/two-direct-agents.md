---
type: regex
target: trace
flags: m
match: 'count:2'
pattern: '^[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"parent_tool_use_id\\?":null'
---
Exactly two agents are launched from the main session.
