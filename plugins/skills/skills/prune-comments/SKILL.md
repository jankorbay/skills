---
name: prune-comments
description: Researches a repository's code comments part by part with read-only subagents, reports which ones to delete (obsolete, redundant, session notes, commented-out code) and which carry information an agent needs, then deletes only what the user approves. Use for a one-off cleanup of comment clutter in a codebase or one feature of it.
argument-hint: "[path or feature]"
disable-model-invocation: true
---

# Prune comments

A one-off cleanup pass over the comments in `$ARGUMENTS` (the whole repo when empty). Research first: **change no file until the user approves the report in Step 4.**

Comments are fine when they carry information. The test for every comment:

> **Would an agent editing this code make a mistake without this comment?** Yes → keep it. No → delete it.

Clear code beats comments. A comment that explains *what* the code does is either redundant (delete it) or a sign the code isn't clear enough (flag it as UNCLEAR). The goal is fewer comments, not comments moved elsewhere. An ADR (architecture decision record) is rare; zero new ADRs is a normal outcome.

## Buckets

| Bucket | What it covers | Action |
|---|---|---|
| **DELETE** | Obsolete (no longer matches the code), redundant (repeats what names, types or code say), session notes ("moved from X", "now that Y is extracted", "previously"), commented-out code, docblocks that only repeat parameter names, issue references outside a TODO (`// see #482`, `// JIRA-1234`), section dividers, step narration in tests ("arrange", "act") | Delete after approval |
| **SUSPECT** | The comment and the code disagree, and the code may be the wrong one | Don't touch. Report as a possible bug |
| **UNCLEAR** | Explains *what* code does that can't be read without it | Don't touch. Report with the code fix that would make the comment unnecessary: a better name, an extracted function, a named constant |
| **KEEP** | Passes the test: ordering rules ("must run before `initAuth()`"), workarounds for library quirks, the meaning of a magic value, a short pointer to an ADR that still governs this code (`// See docs/adr/0007-event-sourcing.md`), a TODO that references a GitHub issue | Keep. Shorten if long. Drop any issue reference from a non-TODO comment, keep the reason |
| **TODO** | A `TODO`, `FIXME`, `HACK` or `XXX` marker without a GitHub issue reference | Don't touch. List for the user, who decides per item: delete it, or open an issue and add its reference |
| **ADR** | A decision that passes all three ADR tests | Propose an ADR; once it exists, the comment becomes a one-line pointer to it |

A TODO with a GitHub issue reference is the only comment allowed to reference an issue. A pointer to an ADR that no longer exists or no longer applies is obsolete.

When a comment explains *why*, it is never a plain DELETE: it is KEEP, SUSPECT or ADR, unless the why is now false (obsolete).

**Never touch:**

- Comments a tool reads. They are input, not notes, and deleting one changes behavior that tests may not catch. Examples: `phpcs:ignore`, `@phpstan-*`, Rector and Psalm annotations, `eslint-disable`, `@ts-expect-error`, `# noqa`, `# type: ignore`, `//go:generate`, build tags, `webpackChunkName`, doctests, docstrings a program reads at runtime (CLI help, API schema descriptions), and doc types richer than the native type (`@param array<int, User>`, JSDoc `@type` in plain JS). When unsure whether a tool reads it, treat it as tool-read.
- Shebangs, license and copyright headers.
- Doc comments on public or published APIs: list them in the report and change them only if the user says so.

## ADRs

Propose an ADR only when all three hold: the decision is **hard to reverse**, **surprising without context**, and **the result of a real trade-off**. A "why" comment that fails any test stays a short KEEP comment, or is deleted if an agent wouldn't need it.

Before writing an ADR, load the `domain-modeling` skill and follow its ADR format (`ADR-FORMAT.md`). If that skill isn't installed, read https://github.com/mattpocock/skills/blob/abeeaf95660ba9e8b7c753eb38f441ca707a8823/skills/engineering/domain-modeling/ADR-FORMAT.md. If the repo already has ADRs, follow its folder and format.

## Step 1: Split into parts

Map the scope into parts by logic, not file count: feature modules, domains, packages, the data layer, the UI layer, shared utilities, scripts, tests. Each part must fit in one reviewer's head; split any that doesn't.

Skip generated files, vendored code, build output and lockfiles.

Count comment lines per part (`cloc --by-file --json` if installed, otherwise an estimate from comment markers). The numbers are for the report only, not a target.

Show the user the part list in a few lines: part, paths, comment lines. **More than 8 parts → wait for the user's go**, since each part costs one subagent. Otherwise continue.

## Step 2: Review each part

Use one subagent per part, all in parallel. A scope of a handful of files: review it yourself instead.

Give each subagent:

- its part's paths
- this skill's keep test, [Buckets](#buckets) section and the three ADR tests (copy them in; the subagent can't see this file)
- a one-line description of each neighbouring part, so it recognises comments about code outside its part
- the instruction: **read-only, edit no file**

Each subagent reads every comment with the code around it and returns one row per comment: `file:line`, bucket, a one-line reason, and for a shortened KEEP the new text.

## Step 3: Merge

- Re-check every ADR candidate against the three tests yourself, and demote any that fail to KEEP or DELETE.
- Merge duplicate ADR candidates across parts: one decision, one ADR, listing every path it governs.
- Spot-check about 10 DELETE rows per part against the code. More than one wrong → re-run that part.

## Step 4: Report in chat, then stop

In this order:

1. A per-part table: comment lines now, after the proposed changes, and the count per bucket.
2. **SUSPECT**, in full: `file:line`, the comment, why the code may be wrong.
3. **TODO** items without an issue, in full.
4. **ADR** proposals, in full: title, the decision in one sentence, one line per ADR test, the paths it governs.
5. **UNCLEAR**, in full: `file:line` and the proposed code fix, grouped by part. This is the to-do list for a later refactor.
6. Public API doc comments, if any, for a decision.
7. **KEEP** shortenings: count, plus 2–3 before → after examples.
8. **DELETE**: counts per file with 2–3 examples each. Give the full list only if asked.

Ask what to apply. The user may approve everything, exclude rows, or change buckets.

## Step 5: Apply what was approved

1. Delete and shorten the approved comments. Touch nothing but comments.
2. Write each approved ADR, then replace the comments it covers with a one-line pointer to it.
3. For each TODO the user wants kept, open the issue (`gh issue create`) and add its reference to the TODO.
4. Verify by reading `git diff`: every removed line is a comment, and the only added lines are shortened comments, ADR pointers, TODO issue references and ADR files. Fix anything else.
5. Run the repo's lint, static analysis and tests. A comment-only change passes unchanged. A new failure means something other than a comment changed: find it and restore it.

Commit only if the user asks: one commit per part where that keeps commits readable.

Never fix SUSPECT, UNCLEAR or TODO items as part of this pass: the pass changes comments only.

## Step 6: Summary

- Comment lines before and after.
- What was deleted, shortened and moved to ADRs.
- The open SUSPECT, UNCLEAR and TODO items.
- **Offer, don't make,** one change that stops the same clutter from coming back, fitted to this repo: a short addition to its AI agent configuration naming the comment kinds that were most common, or, where an existing linter or test can catch a kind (for example issue references outside TODOs), that check instead.
