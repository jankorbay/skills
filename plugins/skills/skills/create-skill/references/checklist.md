# Skill quality checklist

The single rule set used both when creating a skill and when reviewing one. Each rule has an ID, a severity, and a check type.

- **Severity**: 🔴 `blocking` (the skill fails to load, trigger, or run as intended) · 🟡 `should-fix` (works, but measurably worse) · ⚪ `nit` (polish)
- **Check**: `auto` = reported by `scripts/lint_skill.py`; `judgment` = needs reading and reasoning

## Contents
- Frontmatter
- Name
- Description
- Invocation and Claude Code behavior
- Body and structure
- Content
- Scripts and code
- Testing

## Frontmatter

| ID | Sev | Check | Rule |
|---|---|---|---|
| FM001 | 🔴 | auto | Frontmatter starts on line 1 with `---`, closes with `---`, and parses as a YAML mapping. Malformed YAML loads the skill with empty metadata, so it never auto-triggers. |
| FM002 | 🟡 | auto | No unknown keys. Claude Code silently ignores them (common typo: `disable_model_invocation` instead of `disable-model-invocation`). |
| FM003 | ⚪ | auto | Claude Code–only keys are a deliberate choice. Outside Claude Code (claude.ai upload, Skills API) only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are accepted, and any other key is a hard error on upload. |

## Name

| ID | Sev | Check | Rule |
|---|---|---|---|
| N001 | 🔴 | auto | `name` uses only lowercase letters, digits, and single hyphens. Portable skills must set it; Claude Code falls back to the directory name. |
| N002 | 🔴 | auto | `name` is at most 64 characters. |
| N003 | 🔴 | auto | `name` contains neither `anthropic` nor `claude`. |
| N004 | 🟡 | auto | `name` matches the skill's directory name. |
| N005 | 🟡 | judgment | The name says what the skill does. Gerund (`processing-pdfs`), noun phrase (`pdf-processing`), or action form (`process-pdfs`) are fine. Use one pattern across a collection, and prefer the action form for skills users type as `/commands`. Avoid vague names (`helper`, `utils`, `tools`, `data`, `files`). |

## Description

The description is the only thing Claude sees when choosing among possibly 100+ skills. It decides whether the skill is ever used.

| ID | Sev | Check | Rule |
|---|---|---|---|
| D001 | 🔴 | auto | `description` is present and non-empty. |
| D002 | 🔴 | auto | `description` is at most 1,024 characters. |
| D003 | 🔴 | auto | No XML tags in `name` or `description`. |
| D004 | 🟡 | auto | `description` + `when_to_use` is at most 1,536 characters; Claude Code truncates the listing entry beyond that. Put the key use case first. |
| D005 | 🟡 | auto | Written in third person ("Processes Excel files…"), not "I can…" or "You can use this…". The description is injected into the system prompt, and mixed point of view hurts discovery. |
| D006 | 🟡 | auto + judgment | States both **what** the skill does and **when** to use it, for example with a "Use when…" clause. |
| D007 | 🟡 | judgment | Specific, with the key terms users actually say: file types, tools, domain words. Not "Helps with documents". |
| D008 | 🟡 | judgment | Doesn't overlap with another installed skill's triggers. If two descriptions match the same request, Claude picks unpredictably. Narrow one, merge them, or make one manual-only. |
| D009 | ⚪ | judgment | Confident but not "pushy". State concrete triggers rather than "ALWAYS use this skill whenever…". Over-broad wording causes false triggers and competes with other skills. |

## Invocation and Claude Code behavior

| ID | Sev | Check | Rule |
|---|---|---|---|
| I001 | 🔴 | auto | `disable-model-invocation: true` and `user-invocable: false` are not both set; that combination leaves no way to run the skill. |
| I002 | 🟡 | judgment | A skill with side effects (deploys, commits, sends messages, edits many files) sets `disable-model-invocation: true` so it only runs when a user types it. |
| I003 | 🟡 | judgment | Pure background knowledge that isn't a meaningful action sets `user-invocable: false`. |
| I004 | 🟡 | judgment | `allowed-tools` pre-approves only what the skill needs, scoped narrowly (`Bash(git status *)`, not `Bash`). It grants permissions; it doesn't restrict other tools (that's `disallowed-tools`). On a skill Claude loads automatically, `allowed-tools` makes loading the skill itself need the user's approval, and non-interactive runs deny it. Prefer it on user-invoked skills. |
| I005 | 🟡 | judgment | `context: fork` is used only for skills with an explicit task. The forked subagent doesn't see the conversation, and guidelines-only content produces nothing useful there. |
| I006 | 🟡 | judgment | Skills that take input use `$ARGUMENTS` / `$0` or named `arguments`, and set `argument-hint`. |
| I007 | 🟡 | judgment | Bundled files are referenced through `${CLAUDE_SKILL_DIR}` (or `${CLAUDE_PLUGIN_ROOT}` in plugins) wherever a command runs, because the working directory is the user's project, not the skill directory. |
| I008 | 🟡 | judgment | Rules that must hold every time, such as "never edit X" or "always run Y after editing", are enforced with a hook (skill `hooks` frontmatter), not prose alone. |
| I009 | ⚪ | judgment | `` !`command` `` injections tolerate failure (`|| true`) when failure is expected. A non-zero exit aborts the whole invocation. |

## Body and structure

| ID | Sev | Check | Rule |
|---|---|---|---|
| B001 | 🟡 | auto | SKILL.md body is under 500 lines. Move detail into reference files. |
| B002 | 🔴 | auto | Every relative link in SKILL.md points to a file that exists. |
| B003 | 🟡 | auto | References are one level deep: files linked from SKILL.md don't link on to further local `.md` files. Claude may only partially read nested references. |
| B004 | 🟡 | auto | Reference files longer than 100 lines start with a table of contents. |
| B005 | 🟡 | auto | Paths use forward slashes only. |
| B006 | 🟡 | judgment | SKILL.md is an overview that says *when* to read each reference file. References are organized by domain or feature, with descriptive file names (`reference/finance.md`, not `doc2.md`). |
| B007 | 🟡 | judgment | The most important instructions are near the top. After compaction Claude Code keeps only the first ~5,000 tokens of an invoked skill. |

## Content

| ID | Sev | Check | Rule |
|---|---|---|---|
| C001 | 🟡 | judgment | Concise. Claude is already smart, so cut explanations of things it knows (what a PDF is, how libraries work). Each paragraph must justify its tokens. |
| C002 | 🟡 | judgment | Degrees of freedom match the task's fragility: high (text guidance) when many approaches work, medium (template or pseudocode with parameters) when a pattern is preferred, low (exact command, "do not modify") when steps are fragile or order matters. |
| C003 | 🟡 | judgment | Complex tasks are numbered steps, with a copyable progress checklist for long workflows and a validate → fix → repeat loop for quality-critical output. |
| C004 | 🟡 | judgment | One default approach with an escape hatch, not a menu of equivalent options. |
| C005 | 🟡 | judgment | Consistent terminology: one term per concept throughout. |
| C006 | 🟡 | judgment | Examples are concrete (input → output pairs) where output quality depends on style. |
| C007 | ⚪ | auto + judgment | No time-sensitive statements ("before August 2025…"). Put superseded approaches in a collapsed "Old patterns" section. |
| C008 | ⚪ | judgment | Explain *why* behind important rules rather than relying on bare ALWAYS/NEVER. Keep strong words for the rules that really are absolute. |
| C009 | 🟡 | judgment | MCP tools are named fully qualified, as `ServerName:tool_name`. |
| C010 | 🔴 | judgment | No surprising behavior. The skill does what its description says, with no hidden data exfiltration, unrelated actions, or misleading intent. |

## Scripts and code

| ID | Sev | Check | Rule |
|---|---|---|---|
| S001 | 🟡 | judgment | Deterministic or fragile operations (validation, parsing, transforms) are bundled scripts, not code Claude regenerates each time. |
| S002 | 🟡 | judgment | Scripts handle errors themselves with specific messages ("Field 'x' not found. Available: a, b") rather than failing and leaving Claude to guess. |
| S003 | ⚪ | judgment | No "voodoo constants": every timeout, limit, or retry count is justified in a comment. |
| S004 | 🟡 | judgment | SKILL.md says whether to **run** a script or **read** it as reference. |
| S005 | 🟡 | judgment | Required packages are listed, and their availability is checked or degraded gracefully. |

## Testing

| ID | Sev | Check | Rule |
|---|---|---|---|
| T001 | 🟡 | judgment | At least three realistic evaluation scenarios exist, written before or alongside the skill, covering the gaps the skill is meant to fill. |
| T002 | 🟡 | judgment | Tested on the models it will run on: Haiku (is guidance sufficient?), Sonnet (clear and efficient?), Opus (not over-explained?). |
| T003 | ⚪ | judgment | Trigger behavior is tested: realistic prompts that should and should not load it, including near-misses. |
