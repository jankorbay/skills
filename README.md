# Jan Korbay's Skills

Skills for [Claude Code](https://code.claude.com), packaged as a plugin and installable from this repository's marketplace.

## Installation

Add this repository as a marketplace, then install the plugin:

```bash
claude plugin marketplace add jankorbay/skills
claude plugin install skills@jankorbay-skills
```

Or do both in one step:

```bash
claude plugin install skills --marketplace jankorbay/skills
```

Inside a Claude Code session, the same commands work as `/plugin marketplace add jankorbay/skills` and `/plugin install skills@jankorbay-skills`.

The plugin installs for your user by default (all projects). To share it with a project's team through the repo's `.claude/settings.json`, add `--scope project`.

### Updating

The plugin has no pinned version, so every commit to `main` is a new release:

```bash
claude plugin marketplace update jankorbay-skills
claude plugin update skills@jankorbay-skills
```

### Uninstalling

```bash
claude plugin uninstall skills@jankorbay-skills
claude plugin marketplace remove jankorbay-skills
```

## Skills

Plugin skills are namespaced: type them as `/skills:<skill-name>`.

| Skill | Invocation | Description |
|---|---|---|
| [`create-skill`](plugins/skills/skills/create-skill/SKILL.md) | `/skills:create-skill [what it should do]`, or Claude loads it automatically when you ask to create a skill | Creates and edits skills following Anthropic's current skill-authoring best practices and Claude Code's skill features (invocation control, arguments, allowed-tools, forked context). Includes a linter for the mechanical rules. |
| [`review-skills`](plugins/skills/skills/review-skills/SKILL.md) | `/skills:review-skills [scope]` (manual only) | Audits your skills, proposes concrete fixes, iterates on them with you, and applies only the ones you approve, until you're satisfied. |

### `create-skill` and Anthropic's `skill-creator`

`create-skill` overlaps with Anthropic's own [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator). Both trigger when you ask Claude to create a skill, so with both installed Claude may pick either one. `create-skill` adds:

- **Current guidance**: it follows Anthropic's latest [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) where `skill-creator` differs. Examples: third-person, specific descriptions instead of "pushy" ones; a table of contents for references over 100 lines, not 300; no `claude`/`anthropic` in names; one-level-deep references; degrees of freedom; testing across Haiku, Sonnet, and Opus.
- **Claude Code features**: `disable-model-invocation`, `user-invocable`, arguments, `${CLAUDE_SKILL_DIR}`, `allowed-tools`, `` !`command` `` injection, `context: fork`, hooks, and when to use each. `skill-creator`'s validator rejects these fields.
- **A shared rule set**: the same [checklist](plugins/skills/skills/create-skill/references/checklist.md) is enforced by `review-skills`.

`skill-creator` remains the better tool for benchmark-style evals and automated description optimization. To keep only one creator active, disable the other in `/plugin`.

### `review-skills` scopes

```text
/skills:review-skills                  # asks which scope to review
/skills:review-skills project          # .claude/skills/ in the current repo (and plugin skills if the repo is a plugin)
/skills:review-skills user             # your personal skills in ~/.claude/skills/
/skills:review-skills plugin <name>    # an installed plugin's skills (edits its source, not the cache)
/skills:review-skills create-skill     # one skill by name or path
/skills:review-skills all              # project + user
```

## Repository layout

```text
.claude-plugin/marketplace.json     # marketplace "jankorbay-skills"
plugins/skills/                     # plugin "skills"
├── .claude-plugin/plugin.json
└── skills/
    ├── create-skill/
    │   ├── SKILL.md
    │   ├── references/             # checklist, frontmatter, writing guide, testing, sources
    │   └── scripts/lint_skill.py   # mechanical rule checker
    └── review-skills/
        └── SKILL.md
```

## Development

Lint all skills and validate the manifests (CI runs the same checks on every push and pull request):

```bash
python3 plugins/skills/skills/create-skill/scripts/lint_skill.py plugins/
claude plugin validate .
```

To try local changes without pushing: `claude plugin marketplace add ./` from the repo root, then install as above.

## License

[MIT](LICENSE)
