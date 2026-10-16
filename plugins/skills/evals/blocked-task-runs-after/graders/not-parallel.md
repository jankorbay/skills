---
type: regex
target: trace
flags: m
match: 'not_contains'
pattern: '^[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"parent_tool_use_id\\?":null|\\?"id\\?":\\?"(msg_\w+)\\?"[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"parent_tool_use_id\\?":null[^\n]*\n(?:[^\n]*\n)*?[^\n]*\\?"id\\?":\\?"\1\\?"[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"'
---
The two steps are not launched in the same message.
