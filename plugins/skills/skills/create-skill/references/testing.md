# Testing a skill

## Contents
- Evaluation-first workflow
- Writing scenarios
- Claude A / Claude B iteration
- Testing across models
- Testing triggering
- Automated evals with claude plugin eval

## Evaluation-first workflow

Write evaluations **before** writing much documentation, so the skill solves observed problems rather than imagined ones:

1. **Find the gaps**: run the representative tasks without the skill and note exactly where Claude fails or needs to be told something.
2. **Write at least three scenarios** that exercise those gaps.
3. **Record the baseline**: how Claude does without the skill.
4. **Write minimal instructions** that close the gaps.
5. **Iterate**: re-run, compare with the baseline, refine.

## Writing scenarios

Make prompts realistic: the way a user would actually type them, with concrete details (file names, numbers, context), not "process this file".

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads the PDF with a suitable library or CLI tool",
    "Extracts text from every page",
    "Writes readable text to output.txt"
  ]
}
```

Store scenarios next to the skill (e.g. `evals/`) so later edits can be re-checked.

## Claude A / Claude B iteration

- **Claude A** (this session) helps write and refine the skill.
- **Claude B** (a fresh session or subagent with only the skill loaded) uses it on real tasks.

Watch Claude B. Does it read files in an unexpected order? Miss a reference? Re-read one file constantly (move that content into SKILL.md)? Never open a bundled file (remove it or signal it better)? Bring specific observations back to Claude A ("B forgot to filter by date"), apply the change, and test again.

## Testing across models

The same skill behaves differently per model. Test on every model it will run on:

- **Haiku**: is there enough guidance?
- **Sonnet**: is it clear and efficient?
- **Opus**: does it over-explain?

## Testing triggering

For auto-invoked skills, check the description with realistic prompts:

- 8–10 that **should** trigger, phrased differently, some without naming the skill or file type.
- 8–10 that **should not**, mostly near-misses that share keywords but need something else.

Simple one-step requests may not trigger any skill, because Claude handles them directly. Test with substantive tasks. If the skill doesn't trigger, add the words users say; if it triggers too often, narrow the description or set `disable-model-invocation: true`.

## Automated evals with claude plugin eval

For skills shipped in a plugin, `claude plugin eval` runs each case in an isolated session, with and without the plugin, and reports the score difference (Δ). Every run and judge call uses real model usage.

```text
<plugin>/evals/<case-name>/
├── prompt.md               # the user message (frontmatter: runs, max_turns, …)
└── graders/
    ├── skill-fired.md      # did the skill load?
    └── criteria.md         # was the result right?
```

`graders/skill-fired.md`:

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"'
---
```

`graders/criteria.md`: an `llm` grader whose body lists concrete PASS and FAIL conditions. Free graders (`regex`, `tool_used`, `tool_order`, `file_exists`) cost nothing; `llm` and `baseline` call a judge model.

Commands, run from the plugin root:

- `claude plugin eval init`: interactively proposes cases and graders.
- `claude plugin eval .`: runs the suite and writes an HTML report.
- `claude plugin eval . --case <name> --runs 1`: one quick case.

A Δ near zero with `skill-fired` failing means Claude isn't choosing the skill. Fix the description and re-run.

Anthropic's skill-creator plugin has its own `evals/evals.json` format; the two tools don't read each other's files.
