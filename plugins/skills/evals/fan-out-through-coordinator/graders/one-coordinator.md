---
type: regex
target: trace
flags: m
match: 'count:1'
pattern: '^[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"parent_tool_use_id\\?":null'
---
The main session launches exactly one agent: the coordinator.
