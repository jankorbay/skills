---
type: regex
target: trace
flags: m
pattern: '^[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"parent_tool_use_id\\?":null|\\?"id\\?":\\?"(msg_\w+)\\?"[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"[^\n]*\\?"parent_tool_use_id\\?":null[^\n]*\n(?:[^\n]*\n)*?[^\n]*\\?"id\\?":\\?"\1\\?"[^\n]*\\?"name\\?":\\?"(?:Task|Agent)\\?"'
---
Both agents are launched in the same assistant message.
