---
name: create-skill
description: Creates and edits Agent Skills (SKILL.md) following Anthropic's current skill-authoring best practices and Claude Code's skill features such as invocation control, arguments, allowed-tools, and forked context. Use when creating a new skill, turning a workflow into a skill, writing or restructuring a SKILL.md, writing a skill description, or deciding whether a skill should be user-invoked, model-invoked, or both.
argument-hint: "[what the skill should do]"
---

# Create a skill

Build skills that are small, discoverable, and tested. The rules come from Anthropic's skill-authoring best practices and the Claude Code skills reference. Where Anthropic's older `skill-creator` guidance differs (for example "pushy" descriptions), follow this skill; see [references/sources.md](references/sources.md).

Arguments, if invoked as a command: $ARGUMENTS

Copy this checklist and track progress:

```
- [ ] 1. Capture intent
- [ ] 2. Find the gaps and write 3+ scenarios
- [ ] 3. Choose location, name, and invocation
- [ ] 4. Write the description
- [ ] 5. Write the body and bundled files
- [ ] 6. Validate
- [ ] 7. Test and iterate
```

## 1. Capture intent

If the conversation already contains the workflow ("turn this into a skill"), extract the steps, tools, corrections, and output formats from it first. Then ask the user only what's still missing:

- What should the skill let Claude do, and what does a good result look like?
- When should it be used, in what words would a user ask?
- Does it have side effects (deploys, commits, messages, bulk edits)?
- Where must it run: Claude Code only, or also claude.ai / the API (portable)?

## 2. Find the gaps and write scenarios

A skill should add only what Claude doesn't already know. Identify where Claude without the skill would fail or need to be told something: conventions, schemas, fragile sequences, preferences. Write at least three realistic scenarios covering those gaps before writing much content. See [references/testing.md](references/testing.md).

## 3. Choose location, name, and invocation

**Location**: personal `~/.claude/skills/<name>/`, project `.claude/skills/<name>/`, or a plugin's `skills/<name>/`. If the current repository is a plugin or marketplace, follow its conventions (CLAUDE.md, README skill list).

**Name**: lowercase letters, digits, hyphens; at most 64 characters; no `anthropic` or `claude`; same as the directory name; one naming pattern across the collection.

**Invocation**, by side effects:

| Situation | Frontmatter |
|---|---|
| Safe for Claude to start on its own | default (both user and Claude can invoke) |
| Side effects, or a user-paced interactive flow | `disable-model-invocation: true` |
| Background knowledge, not a command | `user-invocable: false` |

Never combine `disable-model-invocation: true` with `user-invocable: false`. For portable skills, use only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. All other fields: [references/frontmatter.md](references/frontmatter.md).

## 4. Write the description

This is what Claude uses to decide whether to load the skill, so it matters more than any other line.

- Third person: "Generates…", not "I can…" or "You can use this…".
- What it does **and** when to use it ("Use when…"), with the words users actually say.
- Lead with the key use case; at most 1,024 characters.
- Specific, not pushy. Concrete triggers, no "ALWAYS use for anything involving…".
- No overlap with other installed skills. Compare against the skills listed in this session and narrow the wording if two would match the same request.

## 5. Write the body and bundled files

- **Concise**: assume Claude is smart. Cut anything it would do correctly anyway.
- **Degrees of freedom**: prose for judgment calls, templates for preferred patterns, exact commands for fragile steps.
- **Structure**: SKILL.md under 500 lines, as an overview that says when to read each reference file. References one level deep, a "Contents" section in files over 100 lines, forward slashes, the most important instructions first.
- **Workflows**: numbered steps, a copyable checklist for long tasks, validate → fix → repeat loops for quality-critical output.
- **Scripts** for deterministic work. Run them via `${CLAUDE_SKILL_DIR}/scripts/…`, say whether to run or read, handle errors with actionable messages, and justify constants.
- **Hygiene**: no time-sensitive statements, consistent terminology, concrete examples, explain *why*, fully qualified MCP tool names (`Server:tool`).

Patterns and examples: [references/writing-guide.md](references/writing-guide.md).

## 6. Validate

Run the linter on the new skill and fix every 🔴 and 🟡 finding:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/lint_skill.py <path-to-skill>
```

It checks the mechanical rules: frontmatter, name, description limits and voice, invocation conflicts, body length, broken or nested links, tables of contents, and paths. For a plugin, also run `claude plugin validate <plugin-or-marketplace-root>`.

Then review the judgment rules (D007–D009, I002–I009, B006–B007, C001–C010, S001–S005) against [references/checklist.md](references/checklist.md).

## 7. Test and iterate

Run the scenarios from step 2 with the skill loaded, ideally in a fresh session or subagent. Compare with the baseline, observe where Claude struggles, and refine. Test on every model the skill will run on (Haiku, Sonnet, Opus), and check triggering with prompts that should and shouldn't load it. For plugin skills, `claude plugin eval` automates this. See [references/testing.md](references/testing.md).

Finish by showing the user the final file tree, the description, and the scenarios. If the skill lives in a repository with a skill list (README), update it.
