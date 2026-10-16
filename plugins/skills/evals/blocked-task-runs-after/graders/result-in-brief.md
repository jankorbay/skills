---
type: regex
target: trace
flags: m
pattern: '^[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*(?:abs\(|absolute)[^\n]*(?:test)[^\n]*\\?"parent_tool_use_id\\?":null|^[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*test[^\n]*(?:abs\(|absolute)[^\n]*\\?"parent_tool_use_id\\?":null'
---
A later agent's brief carries the step-1 conclusion (abs / absolute).
