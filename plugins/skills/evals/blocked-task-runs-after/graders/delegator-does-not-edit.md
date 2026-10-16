---
type: regex
target: trace
flags: m
match: 'not_contains'
pattern: '^[^\n]*\\?"name\\?":\\?"(?:Edit|Write|NotebookEdit)\\?"[^\n]*\\?"parent_tool_use_id\\?":null'
---
The delegator never edits files itself.
