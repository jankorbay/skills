# Frontmatter and Claude Code behavior

## Contents
- Portable vs Claude Code-only fields
- Field reference
- Choosing who can invoke the skill
- Arguments and substitutions
- Dynamic context injection
- Running in a forked subagent
- Where skills live
- Lifecycle facts that affect authoring

## Portable vs Claude Code-only fields

Decide first where the skill must run:

- **Portable** (claude.ai upload, Skills API, Claude Code): only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Any other key is a hard error on upload. `name` and `description` are required.
- **Claude Code only** (personal, project, or plugin skills): every field below is available. Unknown keys are silently ignored, so spell them exactly, with hyphens (`disable-model-invocation`, not `disable_model_invocation`).

Frontmatter must start on line 1. If the YAML doesn't parse, Claude Code loads the body with empty metadata: `/name` still works, but Claude never auto-triggers it. Run `claude plugin validate <skills-dir>` or `scripts/lint_skill.py` to catch this.

## Field reference

| Field | Effect |
|---|---|
| `name` | Lowercase letters, digits, hyphens; at most 64 characters; no `anthropic`/`claude`. Becomes `/name` (or `/plugin:name`). Defaults to the directory name in Claude Code. |
| `description` | What it does + when to use it; at most 1,024 characters, third person, no XML tags. The only text Claude sees when choosing skills. |
| `when_to_use` | Extra trigger text appended to `description`. The combined listing entry is truncated at 1,536 characters. |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` or `[project\|user\|<path>]`. |
| `arguments` | Named positional args (space-separated string or list), available as `$name`. |
| `disable-model-invocation` | `true`: only the user can run it (`/name`). Description is not loaded into context. Also blocks subagent preloading and scheduled tasks. |
| `user-invocable` | `false`: hidden from the `/` menu; only Claude can load it. |
| `allowed-tools` | Pre-approves tools for the invoking turn (e.g. `Bash(git diff *)`). Doesn't restrict other tools, and the grant clears on the user's next message. On an automatically loaded skill, it makes loading the skill itself need the user's approval (observed in Claude Code 2.1.296), so prefer it on user-invoked skills. |
| `disallowed-tools` | Removes tools from Claude's pool while the skill is active. |
| `model` | Model override for the current turn (`inherit` keeps the active one). |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max`. |
| `context` | `fork` runs the skill in a subagent (see below). |
| `agent` | Subagent type for `context: fork` (`Explore`, `Plan`, `general-purpose`, or a custom agent). |
| `background` | With `fork`: `false` waits for the result in the invoking turn. Default `true`. |
| `hooks` | Hooks registered when the skill is invoked, active for the rest of the session. Use them for rules that must hold every time. |
| `paths` | Glob patterns; auto-activation only when matching files are involved. |
| `shell` | `bash` (default) or `powershell` for `` !`command` `` blocks. |
| `license`, `compatibility`, `metadata` | Spec fields; Claude Code accepts them but ignores them. |

Booleans accept `true/false`, `yes/no`, `on/off`, `1/0`.

## Choosing who can invoke the skill

| Setting | User runs `/name` | Claude auto-loads | Use for |
|---|---|---|---|
| default | yes | yes | Most skills: knowledge plus actions that are safe to start automatically |
| `disable-model-invocation: true` | yes | no | Side effects or user-paced workflows: deploy, commit, send, bulk edits, interactive reviews |
| `user-invocable: false` | no | yes | Background knowledge that isn't a meaningful command (conventions, schemas) |

Never set both `disable-model-invocation: true` and `user-invocable: false`: nothing could run the skill.

In plugins, users type `/plugin-name:skill-name`. Auto-loading is unaffected by the prefix.

## Arguments and substitutions

| Variable | Expands to |
|---|---|
| `$ARGUMENTS` | Everything typed after the command. If the body has no placeholder, Claude Code appends `ARGUMENTS: <value>`. |
| `$ARGUMENTS[N]`, `$N` | 0-based positional argument. Quote multi-word values: `/x "a b" c`. |
| `$name` | Named argument from `arguments`. |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md. Use it in every command that runs a bundled script, because the working directory is the user's project. |
| `${CLAUDE_PLUGIN_ROOT}` | Plugin install directory (plugin skills only). Use it to reach files shared by several skills in one plugin. |
| `${CLAUDE_PLUGIN_DATA}` | Persistent per-plugin data directory, kept across updates. |
| `${CLAUDE_PROJECT_DIR}` | The project root. |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Session ID, current effort level. |

Escape a literal dollar sign as `\$`. On user-invoked skills, pair a bundled script with a narrow pre-approval:

```yaml
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/check.py *)
```

## Dynamic context injection

`` !`command` `` runs before the skill reaches Claude, and its output replaces the placeholder. A fenced block opened with ` ```! ` runs a multi-line command.

- A non-zero exit aborts the whole invocation (exit 1 from search/compare commands excepted). Append `|| true` when failure is acceptable.
- Commands go through permission rules; pre-approve them with `allowed-tools`.
- Commands don't run for skills synced from claude.ai, or when `disableSkillShellExecution` is set.

## Running in a forked subagent

`context: fork` makes the rendered skill the task prompt of a fresh subagent. That subagent does **not** see the conversation. Use it only for self-contained tasks (research, audits) whose result is useful on its own; a guidelines-only skill produces nothing there. Forked skills run in the background unless `background: false`.

## Where skills live

| Scope | Path | Notes |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects. Wins over project skills with the same name. |
| Project | `.claude/skills/<name>/SKILL.md` | Committed with the repo, shared with the team. |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` | Sessions in or below that directory. |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Namespaced `/plugin:name`; distributed via a marketplace. |

`~/.claude/skills/synced/` holds skills synced from claude.ai. Edit those on claude.ai, not on disk. Installed plugin copies under `~/.claude/plugins/` are caches that updates overwrite; edit the plugin's source repository instead.

## Lifecycle facts that affect authoring

- The rendered SKILL.md stays in the conversation; Claude doesn't re-read the file on later turns. Phrase standing guidance so it applies to the whole task ("run the tests after every edit").
- After compaction, Claude Code re-attaches only the first ~5,000 tokens of each invoked skill. Put the essential instructions first.
- Claude Code picks up edits to existing skills live. A newly created top-level skills directory needs `/reload-skills`.
- If many skills are installed, descriptions are dropped from the listing to fit a budget (about 1% of the context window), least-used first. Short descriptions with the key use case first survive best. `/skill-doctor` shows which skills never run.
