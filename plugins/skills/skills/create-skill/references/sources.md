# Sources and differences from skill-creator

Last verified against the sources: 2026-10-12 (Claude Code 2.1.296).

## Sources

- Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code skills (frontmatter, invocation, substitutions, troubleshooting): https://code.claude.com/docs/en/skills
- Plugin manifest and marketplace reference: https://code.claude.com/docs/en/plugins/manifest-reference, https://code.claude.com/docs/en/plugins/marketplace-reference
- Plugin evals: https://code.claude.com/docs/en/plugin-evals

If the live documentation disagrees with this skill, and you can fetch it, the live documentation wins. Tell the user which rule changed so the skill can be updated.

## Where this skill differs from Anthropic's skill-creator

Anthropic's `skill-creator` focuses on eval tooling: benchmark runs, a review viewer, and description optimization. It's still the better tool for those. Its authoring guidance differs from the current best practices in these places, and this skill follows the best practices:

| Topic | skill-creator | This skill (current guidance) |
|---|---|---|
| Description tone | Make descriptions "a little bit pushy" | Third person, specific triggers, no over-broad wording (D005, D009) |
| Table of contents in references | For files over 300 lines | For files over 100 lines (B004) |
| Reserved words in `name` | Not checked | No `anthropic` or `claude` (N003) |
| Reference depth | Not covered | One level deep from SKILL.md (B003) |
| Degrees of freedom | Not covered | High / medium / low, matched to fragility (C002) |
| Testing across models | Not covered | Haiku, Sonnet, Opus (T002) |
| Claude Code frontmatter | Its validator rejects any key outside the portable six | Claude Code fields are documented and allowed, with their portability cost made explicit (FM003) |
| Invocation control | Not covered | `disable-model-invocation` / `user-invocable` chosen by side effects (I001–I003) |
| Arguments, `${CLAUDE_SKILL_DIR}`, `` !`cmd` ``, `context: fork`, hooks | Not covered | Covered in references/frontmatter.md |
