# Writing the skill

## Contents
- Naming
- Writing the description
- Conciseness
- Degrees of freedom
- Structure and progressive disclosure
- Workflow patterns
- Output patterns
- Bundled scripts
- Content hygiene

## Naming

Lowercase letters, digits, hyphens; at most 64 characters; no `anthropic` or `claude`. Pick one pattern per collection:

- Gerund (Anthropic's default suggestion): `processing-pdfs`, `writing-documentation`
- Noun phrase: `pdf-processing`
- Action form: `process-pdfs`. It reads best for skills users type, like `/review-skills`.

Avoid vague (`helper`, `utils`, `tools`) and generic (`documents`, `data`, `files`) names. Keep the directory name identical to `name`.

## Writing the description

Claude chooses among all installed skills from name + description alone. Write it in **third person**, saying **what** the skill does and **when** to use it, with the words users actually say.

```yaml
# Good
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Bad: vague, no trigger
description: Helps with documents
# Bad: first/second person
description: I can help you process Excel files
```

Guidelines:

- Lead with the key capability; the listing may be truncated, and descriptions of rarely used skills are dropped first when space is short.
- Name concrete triggers: file types, tools, domain terms, typical phrasings.
- Be confident, not pushy. "Use when…" with specific triggers beats "ALWAYS use this skill for anything involving…". Over-broad wording causes false triggers and collisions with other skills.
- Check for overlap with skills already installed. If another skill's description matches the same requests, narrow one, merge them, or make one manual-only (`disable-model-invocation: true`).
- Keep it under 1,024 characters (and description + `when_to_use` under 1,536 in Claude Code).

## Conciseness

Claude is already very capable, so add only what it doesn't know: your conventions, schemas, fragile sequences, and preferences. For each paragraph ask: "Would Claude get this wrong without it?" If not, cut it.

```markdown
## Extract PDF text
Use pdfplumber:
    with pdfplumber.open("file.pdf") as pdf:
        text = pdf.pages[0].extract_text()
```

That beats three sentences explaining what PDFs are and why pdfplumber is popular.

## Degrees of freedom

Match specificity to how fragile the task is:

| Freedom | Form | When |
|---|---|---|
| High | Prose guidance, heuristics | Many valid approaches; context decides (code review, writing) |
| Medium | Template or pseudocode with parameters | A preferred pattern exists, some variation is fine (reports) |
| Low | Exact command, "do not modify flags" | Fragile, order-critical, or must be consistent (migrations, releases) |

Think of a narrow bridge (exact guardrails) vs an open field (general direction).

## Structure and progressive disclosure

Three loading levels: metadata (always), SKILL.md body (when triggered), bundled files (only when read or run).

- Keep the SKILL.md body under 500 lines. It is an overview that tells Claude **which file to read when**.
- Link every reference file directly from SKILL.md, one level deep. Claude may only skim files reached through another reference.
- Give reference files over 100 lines a "Contents" section at the top, so a partial read still shows the scope.
- Organize by domain or variant (`reference/aws.md`, `reference/gcp.md`) so Claude loads only what applies.
- Use descriptive file names and forward slashes.
- Put the most important instructions first (compaction keeps only the start of a skill).

```text
my-skill/
├── SKILL.md              # overview + workflow + pointers
├── references/
│   ├── api.md            # read when calling the API
│   └── examples.md       # read when unsure about output style
└── scripts/
    └── validate.py       # run, don't read
```

## Workflow patterns

**Numbered steps with a copyable checklist** for long tasks:

````markdown
Copy this checklist and tick items off as you go:
```
- [ ] 1. Analyze the form (run scripts/analyze_form.py)
- [ ] 2. Map fields (edit fields.json)
- [ ] 3. Validate (run scripts/validate_fields.py)
- [ ] 4. Fill and verify
```
````

**Feedback loop** for quality-critical output: run validator → fix → re-run → proceed only when clean. The validator can be a script or a style guide Claude checks against.

**Plan → validate → execute** for batch or destructive changes: write the plan to a file (e.g. `changes.json`), validate it with a script, then apply.

**Conditional workflow** for branching tasks: "Creating new content? → follow A. Editing existing? → follow B." Move large branches into their own reference files.

**Default plus escape hatch** instead of a menu: "Use pdfplumber. For scanned PDFs needing OCR, use pdf2image + pytesseract instead."

## Output patterns

- **Template**: give the exact structure when format matters ("ALWAYS use this template"), or a sensible default ("adapt sections as needed") when it doesn't.
- **Examples**: input → output pairs convey style better than adjectives. Use 2–3 that differ meaningfully.

## Bundled scripts

- Prefer a bundled script over generated code for anything deterministic (validation, parsing, conversion). It is more reliable, uses fewer tokens, and behaves the same every run.
- Say explicitly whether to **run** it ("Run `${CLAUDE_SKILL_DIR}/scripts/x.py`") or **read** it ("See `scripts/x.py` for the algorithm").
- Reference scripts through `${CLAUDE_SKILL_DIR}` in commands, since the working directory is the user's project.
- Handle errors inside the script with actionable messages ("Field 'date' not found. Available: name, total"), rather than failing and leaving Claude to guess.
- Justify constants in comments (`TIMEOUT = 30  # requests usually finish in <30 s`).
- List required packages and fall back gracefully when they're missing; don't assume installs. Prefer the standard library.
- Make output compact and parseable (a `--json` flag helps the skill consume it).

## Content hygiene

- **No time-sensitive statements.** Not "before August 2025 use X". Keep the current method in the main text and older ones in a collapsed `<details>` "Old patterns" section.
- **Consistent terminology**: one term per concept ("field", never also "box" or "element").
- **Explain why.** "Filter test accounts, because they inflate conversion by ~30%" generalizes better than "ALWAYS filter test accounts". Reserve strong wording for absolute rules, and enforce must-always rules with hooks.
- **MCP tools** fully qualified: `ServerName:tool_name`.
- **No surprises**: the skill does what its description says, and nothing hidden.
