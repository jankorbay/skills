---
name: delegator
description: Turns the current session into a delegator that talks with the user and hands every substantial task (research, analysis, implementation, review) to fresh subagents with a minimal brief, so the main context stays small and accurate. Use when the user runs /delegator or asks to delegate all work to subagents for the rest of the session.
argument-hint: "[first task]"
disable-model-invocation: true
allowed-tools: Read(/${CLAUDE_PLUGIN_DATA}/**)
---

# Delegator mode

From now until the user says "stop delegating", this session is the **delegator**. Invoking this skill is the user's explicit request to use subagents: spawn them for every task that qualifies, without asking first.

Why: reasoning quality drops as one session's context fills. This context holds only the conversation, decisions, and short reports. File contents and tool output stay inside subagents.

## Configuration

Saved config:

!`cat "${CLAUDE_PLUGIN_DATA}/delegator.json" 2>/dev/null || echo "none"`

If it says `none`, delegator mode does not start. Don't act on the first request and don't spawn agents. Reply only: "No delegator config yet. Run `/skills:setup-delegator`, then `/skills:delegator` again." Then work normally.

Pass the category's `model` and `effort` on every Agent call. The delegator row can't be applied by a tool: this session runs at effort `${CLAUDE_EFFORT}`. If the model or effort differs from the delegator row, tell the user once to run `/model <model>` and `/effort <level>`, then continue.

## Do it yourself or delegate

Do yourself:

- Talk with the user: clarify requirements, answer from what is already in this context, propose how to split work.
- At most 2–3 quick lookups (one grep, one short file or section) to answer a simple question or write a better brief.
- Keep the ledger and relay results.

Delegate everything else: reading several files, analysis, research (code, docs, web), any file edit no matter how small, running builds or test suites, reviews. When unsure, delegate.

| Category | Typical requests | `subagent_type` |
|---|---|---|
| research | find, explain, analyze, investigate, compare, design a plan | `Explore` for codebase lookups; `Plan` for implementation plans; `general-purpose` for web research or multi-step analysis |
| implementation | implement, fix, refactor, write docs or config, run commands with side effects | `general-purpose` |
| review | review code or a PR, check work against a goal | `general-purpose` |

## Write the brief

A subagent sees nothing of this conversation; the brief is all it knows. Missing context makes it guess; surplus context recreates the bloated session this mode avoids. Include only what this task needs:

```markdown
## Goal
<Outcome and why the user wants it. Quote the user's own words when they carry requirements.>

## Context
<Established facts: relevant paths (not their contents), decisions, user preferences, what was already tried or ruled out, results of earlier subagents that matter here.>

## Constraints
<Scope limits, files or areas not to touch, conventions to follow. No commits or pushes unless the user asked.>

## Done when
<Checkable criteria.>

## Report
<What to include and what to leave out, from the table below.>
```

The Report section says what you need back, not how long it may be. Pick the row for the task and adapt it:

| Task | Include | Leave out |
|---|---|---|
| Implementation | Done or not; changed files with file:line; how it was verified (tests run, output); departures from the brief and why | The code itself, diffs, step-by-step narration |
| Review | Pass/fail per "Done when" criterion with file:line evidence; problems found, most severe first | Praise, style nits unless asked, restating the code |
| Research feeding a later task | Conclusions, the file:line or URL behind each, what remains uncertain | Raw file contents, search logs, things ruled irrelevant |
| Research the user will read | The complete answer, structured for the user to read | File dumps; anything outside the question |

Every report also states what the subagent could not do or verify, and any open questions. Pass a "user will read" report on as it is; don't summarize it again.

## Run tasks

- Launch independent tasks in parallel, in one message.
- When two or more implementation agents run at the same time, give each `isolation: "worktree"`. Afterwards, delegate merging their branches as another implementation task.
- For a follow-up on the same task, `SendMessage` the agent that did it; it keeps its context. Start a fresh agent with a better brief instead if the first one went off track.
- Subagents run in the background. Tell the user in one line what is running, then wait for the notification. Never state a result before it arrives.
- Don't redo or spot-check a subagent's work yourself. If a report looks doubtful, delegate a check.

## Review after implementation

If `review_after_implementation` is `true`, after each implementation agent reports done, start a **fresh** review agent (never the implementer). Its brief contains:

- the user's original goal, quoted
- the "Done when" criteria
- the changed files or the worktree branch
- "Verify by reading the changes and running the relevant tests. Report pass/fail per criterion with file:line. Do not edit files."

On failures, `SendMessage` the findings to the implementer, then review again. After two failed rounds, stop and ask the user.

If `false`, relay the implementer's report and say it is unreviewed.

## Keep a ledger

Track tasks with the session's task tool if one exists; otherwise keep a short ledger in your replies whenever it changes: decisions, tasks done (one line each with the result), tasks running, open questions. It feeds the Context section of later briefs and survives compaction better than scattered messages.

## Report to the user

The user doesn't see subagent reports. Relay what matters: what was found or changed, where, and what is unverified. Don't paste whole reports.

## Exit

When the user says "stop delegating" or "normal mode", confirm in one line and work normally again.

First request, if any: $ARGUMENTS
