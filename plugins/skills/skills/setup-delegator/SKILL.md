---
name: setup-delegator
description: Configures the delegator skill by choosing the model and effort level for the delegator session and for research, implementation, and review subagents, and whether every implementation gets a separate review agent. Use when the user runs /setup-delegator or wants to change delegator models, effort levels, or review settings.
disable-model-invocation: true
allowed-tools:
  - Read(/${CLAUDE_PLUGIN_DATA}/**)
  - Edit(/${CLAUDE_PLUGIN_DATA}/delegator.json)
---

# Set up the delegator

Write the delegator's config to `${CLAUDE_PLUGIN_DATA}/delegator.json`. That directory survives plugin updates.

Current config:

!`cat "${CLAUDE_PLUGIN_DATA}/delegator.json" 2>/dev/null || echo "none"`

## 1. List what's available

- **Models**: the values the Agent tool's `model` parameter accepts in this session (for example `opus`, `sonnet`, `haiku`, `fable`). Next to each alias, show the full model name it maps to, from this session's environment info.
- **Effort**: `low`, `medium`, `high`, `xhigh`, `max`. A model that doesn't support a level falls back to the highest level it supports below it.

## 2. Propose a config

Start from the current config; if it is `none`, use these defaults:

| Category | Model | Effort | Used for |
|---|---|---|---|
| delegator | opus | high | This session: talking, planning, writing briefs |
| research | opus | high | Finding, analyzing, comparing, planning |
| implementation | opus | medium | Writing and editing code, docs, config |
| review | opus | high | Checking work against the user's goal |

If a default model isn't available, propose the most capable one that is.

Show the table, then ask with AskUserQuestion: accept, or edit. To edit, ask which categories to change, then the model and effort for each. Repeat until the user accepts.

## 3. Ask about review after implementation

Ask with AskUserQuestion whether a separate review agent should check every implementation against the original goal. Include this note in the question:

- **Yes**: more accurate. A fresh agent catches missed requirements and false "done" claims the implementer can't see in its own work. It costs about one extra agent run per implementation task, since the reviewer re-reads the changed files and runs tests.
- **No**: fewer tokens. You get the implementer's own report, marked as unreviewed.

## 4. Save

Write the file with exactly this shape:

```json
{
  "delegator": { "model": "opus", "effort": "high" },
  "research": { "model": "opus", "effort": "high" },
  "implementation": { "model": "opus", "effort": "medium" },
  "review": { "model": "opus", "effort": "high" },
  "review_after_implementation": true
}
```

Then tell the user:

- The saved path, and that `/skills:delegator` reads it at start. If delegator mode is already active in this session, use the new values from now on.
- No tool can switch the main session's model, so the delegator row needs `/model <model>` and `/effort <level>`. Pressing Enter in those pickers saves the choice as the default; `s` applies it to this session only.
