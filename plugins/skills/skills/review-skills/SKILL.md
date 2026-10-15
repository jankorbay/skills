---
name: review-skills
description: Reviews existing Agent Skills against Anthropic's current skill-authoring best practices and Claude Code's skill rules, proposes concrete fixes, iterates on them with the user, and applies only the approved ones. Use when the user wants to audit, lint, clean up, or improve their project, personal, or plugin skills.
argument-hint: "[project | user | plugin <name> | <skill-name or path> | all]"
disable-model-invocation: true
allowed-tools:
  - Read(/${CLAUDE_SKILL_DIR}/../create-skill/**)
  - Bash(python3 ${CLAUDE_SKILL_DIR}/../create-skill/scripts/lint_skill.py *)
---

# Review skills

Audit skills, agree on fixes with the user, apply only what they approve, and repeat until they're satisfied. Never edit a file before the user approves the specific finding.

Shared resources (from the `create-skill` skill, installed next to this one):

- Rule set: `${CLAUDE_SKILL_DIR}/../create-skill/references/checklist.md`. Read it fully before reviewing.
- Linter: `python3 ${CLAUDE_SKILL_DIR}/../create-skill/scripts/lint_skill.py <paths…> --json`
- Background, when a finding needs explaining: `references/frontmatter.md` and `references/writing-guide.md` in the same directory.

Scope requested: `$ARGUMENTS`

Copy this checklist and track progress:

```
- [ ] 1. Resolve scope and list the skills
- [ ] 2. Run the linter
- [ ] 3. Judgment review (per skill and across skills)
- [ ] 4. Present findings with proposed fixes
- [ ] 5. Agree on fixes with the user
- [ ] 6. Apply approved fixes
- [ ] 7. Re-check and loop back to 4 until the user is done
- [ ] 8. Summarize
```

## 1. Resolve scope and list the skills

| Argument | Skills to review |
|---|---|
| `project` | `.claude/skills/*/SKILL.md` in the project root and nested `**/.claude/skills/`. If the repo is a plugin or marketplace (has `.claude-plugin/`), also its `skills/` and `plugins/*/skills/`. |
| `user` | `~/.claude/skills/*/SKILL.md`, excluding `synced/` and `.trash/` |
| `plugin <name>` | The named installed plugin's skills (see "Where to edit" below) |
| `<name>` or `<path>` | That one skill, a SKILL.md, or every skill under a directory |
| `all` | `project` + `user` |
| *(empty)* | Ask the user which scope they want, offering the options above |

Show the inventory before reviewing: name, path, body line count, and who can invoke it. If more than about 15 skills are in scope, ask whether to review all of them or a subset.

**Where to edit**: only edit source files the user owns.

- `~/.claude/skills/synced/…` comes from claude.ai and is overwritten on sync. Review it, but propose the changes for the user to make on claude.ai.
- Installed plugins under `~/.claude/plugins/` are caches. Run `claude plugin list --json`. If the plugin's `readFromFolder` is outside `~/.claude/plugins/`, that folder is the editable source. Otherwise ask the user for a local checkout of the plugin's repository. Without one, review read-only and give the fixes as patches.

## 2. Run the linter

Run the linter once on all skills in scope with `--json`. Its findings are already rule-checked, so don't re-derive them. Do check each one for false positives, though: for example, a time-sensitive phrase inside a quoted example. Drop those and say so in the findings.

## 3. Judgment review

For each skill, read SKILL.md and the files it links. Evaluate every `judgment` rule in the checklist. Keep findings concrete: quote the problematic text and point to `file:line`.

Then look across skills:

- **Trigger collisions (D008)**: compare the descriptions of the skills in scope with each other, and with the other skills available in this session. Flag pairs that would match the same request.
- **Naming consistency (N005)**: one naming pattern across the collection.
- **Duplication**: the same instructions copied into several skills, a candidate for a shared reference or one merged skill.

Don't flag stylistic preferences that no rule backs. Each finding must cite a rule ID.

## 4. Present findings with proposed fixes

Number findings globally and order them by severity: 🔴 blocking, then 🟡 should-fix, then ⚪ nit. Use this format:

````markdown
### <skill-name> (`<path>`)

**1. 🔴 D001: Description missing** · `SKILL.md:2`
Problem: Claude can't decide when to use this skill, so it never auto-triggers.
Fix:
```diff
- description:
+ description: Generates release notes from merged PRs. Use when the user asks for release notes or a changelog.
```
````

Rules for proposed fixes:

- Show the exact new text (a diff or replacement block), not "improve the description".
- Keep each fix minimal: it resolves its finding and changes nothing else.
- Mark fixes that break things for users as **⚠ breaking**: renaming a skill (changes `/name`), changing invocation settings, or removing files other skills link to.
- When a fix needs information only the user has (intended triggers, side effects), ask instead of guessing.

End with a tally (e.g. "2 🔴 · 5 🟡 · 3 ⚪") and the ways the user can respond:

- `approve all` · `approve 1, 3-5` · `approve all 🔴🟡`
- `skip 2` (optionally with a reason)
- `change 4: <what to do instead>`
- `explain 6`

## 5. Agree on fixes with the user

Wait for the user's decision. Revise proposals they want changed and show the revised version again. Repeat until every finding is approved or skipped. Never apply a finding the user hasn't approved, even if it's blocking.

## 6. Apply approved fixes

1. Before the first edit, protect the originals. If the skill is in a git repository, note `git status` so the user can diff or revert. If it isn't, copy the skill directory to a backup location and tell the user where.
2. Apply exactly the approved changes, nothing else.
3. Show a short summary of what changed per file (or `git diff --stat`).

## 7. Re-check and loop

Re-run the linter on the changed skills and re-review the edited parts. Present any remaining or new findings in the step 4 format, continuing the numbering. Go back to step 5. Stop when the user says they're done, or when nothing is left to review.

If a fix changed a description or the core instructions, suggest testing the skill's behavior (realistic prompts, or `claude plugin eval` for plugin skills). A clean lint doesn't show that the skill still triggers and works.

## 8. Summarize

List the fixed findings, the skipped ones (with reasons), and anything left open or deferred (for example, fixes to make on claude.ai or upstream). Remind the user to commit the changes if they're in a repository.
