# Repository conventions

This repo is a Claude Code marketplace (`jankorbay-skills`) holding one plugin (`skills`) at `plugins/skills/`.

- New skills go in `plugins/skills/skills/<skill-name>/SKILL.md`. Use the `create-skill` skill and follow its checklist (`plugins/skills/skills/create-skill/references/checklist.md`).
- Name skills in action form (`create-skill`, `review-skills`), matching the directory name.
- Every skill must have a row in the README "Skills" table: link, invocation (`/skills:<name>`), and a one-sentence description. CI fails if a skill is missing from the README.
- Don't add a `version` to `plugin.json`. Users get every commit on `main`.
- Before committing, run:
  - `python3 plugins/skills/skills/create-skill/scripts/lint_skill.py plugins/` (no 🔴 findings)
  - `claude plugin validate .` (the "No version specified" warning is expected)
- When Anthropic's guidance changes, update `create-skill/references/` and the "Last verified" date in `references/sources.md`.
