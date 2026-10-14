#!/usr/bin/env python3
"""Lint Agent Skills against the mechanical rules in references/checklist.md.

Usage:
    python3 lint_skill.py PATH [PATH ...] [--json]

PATH can be a skill directory, a SKILL.md file, or any directory; directories
are searched recursively for SKILL.md files.

Exit codes: 0 = no blocking findings, 1 = at least one blocking finding,
2 = usage error (bad path).

Only the Python standard library is required. PyYAML is used when installed;
otherwise a minimal frontmatter parser handles the common cases (scalars,
quoted strings, block scalars, simple lists).
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

# Limits come from Anthropic's skill authoring best practices and the Claude
# Code skills reference (sources in references/sources.md).
NAME_MAX = 64
DESCRIPTION_MAX = 1024
LISTING_ENTRY_MAX = 1536  # description + when_to_use; Claude Code truncates beyond this
BODY_MAX_LINES = 500
TOC_THRESHOLD_LINES = 100
# A table of contents has to be visible in a partial read (`head`), so only
# the top of the file is searched for one.
TOC_SEARCH_LINES = 40

PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_CODE_KEYS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context", "agent",
    "background", "hooks", "paths", "shell",
}
KNOWN_KEYS = PORTABLE_KEYS | CLAUDE_CODE_KEYS

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".trash"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_TAG_RE = re.compile(r"</?[A-Za-z][\w:-]*[^<>]*>")
FIRST_PERSON_RE = re.compile(r"\b(I can|I will|I'll|I help|I'm|my job)\b", re.IGNORECASE)
SECOND_PERSON_RE = re.compile(r"^\s*(you|your)\b|\byou can use\b", re.IGNORECASE)
WHEN_RE = re.compile(r"\b(use (it |this )?(when|for|whenever|if)|when(ever)? (the )?(user|you|working|asked))", re.IGNORECASE)
TIME_SENSITIVE_RE = re.compile(
    r"\b(before|after|until|as of|since)\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+20\d\d\b"
    r"|\b(before|after|until|as of)\s+20\d\d\b",
    re.IGNORECASE,
)
QUOTED_RE = re.compile(r"\"[^\"]*\"|“[^”]*”|(?<!\w)'[^']*'(?!\w)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
TOC_RE = re.compile(r"^#+\s*(table of )?contents\b", re.IGNORECASE | re.MULTILINE)
TRUE_VALUES = {True, "true", "yes", "on", "1", 1}
FALSE_VALUES = {False, "false", "no", "off", "0", 0}

BLOCKING, SHOULD_FIX, NIT = "blocking", "should-fix", "nit"


class Finding:
    def __init__(self, rule, severity, file, line, message):
        self.rule, self.severity, self.file, self.line, self.message = rule, severity, file, line, message

    def as_dict(self):
        return {"rule": self.rule, "severity": self.severity, "file": str(self.file),
                "line": self.line, "message": self.message}


# ---------------------------------------------------------------- frontmatter

def split_frontmatter(text):
    """Return (frontmatter_text, body_text, body_start_line) or None if absent."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), i + 2
    return None


def parse_minimal_yaml(text):
    """Small fallback parser for top-level keys when PyYAML is unavailable."""
    result, key, mode, buf = {}, None, None, []

    def flush():
        if key is None:
            return
        if mode in ("|", ">"):
            joiner = "\n" if mode == "|" else " "
            result[key] = joiner.join(s.strip() for s in buf).strip()
        elif mode == "list":
            result[key] = [s.strip()[1:].strip().strip("'\"") for s in buf if s.strip().startswith("-")]
        elif mode == "nested":
            result[key] = "\n".join(buf)

    for raw in text.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            if mode in ("|", ">"):
                buf.append("")
            continue
        top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if top and not raw[0].isspace():
            flush()
            key, value = top.group(1), top.group(2).strip()
            buf = []
            if value in ("|", ">", "|-", ">-", "|+", ">+"):
                mode = value[0]
            elif value == "":
                mode = "nested"
            else:
                mode = None
                closers = {"[": "]", "{": "}"}
                if value[0] in closers and not value.endswith(closers[value[0]]):
                    raise ValueError(f"unclosed flow collection in {key!r}")
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                    value = value[1:-1]
                result[key] = value
        elif raw[0].isspace() and key is not None:
            if mode == "nested" and raw.strip().startswith("-"):
                mode = "list"
            buf.append(raw)
        else:
            raise ValueError(f"cannot parse line: {raw!r}")
    flush()
    return result


def parse_frontmatter(text):
    if yaml is not None:
        data = yaml.safe_load(text) if text.strip() else {}
    else:
        data = parse_minimal_yaml(text)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def line_of(text, needle, offset=1):
    """1-based line number of the first occurrence of needle, or offset."""
    idx = text.find(needle)
    return text.count("\n", 0, idx) + 1 if idx >= 0 else offset


# ---------------------------------------------------------------- checks

def check_skill(skill_md):
    findings = []
    skill_dir = skill_md.parent
    text = skill_md.read_text(encoding="utf-8")

    def add(rule, severity, line, message, file=skill_md):
        findings.append(Finding(rule, severity, file, line, message))

    parts = split_frontmatter(text)
    if parts is None:
        add("FM001", BLOCKING, 1, "No frontmatter: SKILL.md must start with '---' on line 1 and close with '---'.")
        return findings
    fm_text, body, body_start = parts
    try:
        fm = parse_frontmatter(fm_text)
    except Exception as exc:  # report any parse error as a finding, not a crash
        add("FM001", BLOCKING, 2, f"Frontmatter does not parse as YAML ({' '.join(str(exc).split())}). "
            "Claude Code would load the skill with empty metadata, so it never auto-triggers.")
        return findings

    # Frontmatter keys
    for k in fm:
        if k not in KNOWN_KEYS:
            hint = ""
            if k.replace("_", "-") in KNOWN_KEYS:
                hint = f" Did you mean '{k.replace('_', '-')}'?"
            add("FM002", SHOULD_FIX, line_of(text, f"{k}:"), f"Unknown frontmatter key '{k}' is silently ignored.{hint}")
    cc_only = sorted(k for k in fm if k in CLAUDE_CODE_KEYS)
    if cc_only:
        add("FM003", NIT, 2, "Claude Code-only keys (" + ", ".join(cc_only) + "): the skill can't be uploaded "
            "to claude.ai or the Skills API without removing them. Fine if it targets Claude Code only.")

    # Name
    name = fm.get("name")
    if name is None:
        add("N001", SHOULD_FIX, 2, f"No 'name': Claude Code uses the directory name '{skill_dir.name}', "
            "but claude.ai and the Skills API require it.")
    else:
        name = str(name).strip()
        nline = line_of(text, "name:")
        if not NAME_RE.match(name):
            add("N001", BLOCKING, nline, f"Name '{name}' must use only lowercase letters, digits, and single hyphens.")
        if len(name) > NAME_MAX:
            add("N002", BLOCKING, nline, f"Name is {len(name)} characters; maximum is {NAME_MAX}.")
        for word in ("anthropic", "claude"):
            if word in name.lower():
                add("N003", BLOCKING, nline, f"Name contains the reserved word '{word}'.")
        if name != skill_dir.name:
            add("N004", SHOULD_FIX, nline, f"Name '{name}' differs from directory name '{skill_dir.name}'.")
        if XML_TAG_RE.search(name):
            add("D003", BLOCKING, nline, "Name contains an XML tag.")

    # Description
    desc = fm.get("description")
    dline = line_of(text, "description:")
    if desc is None or not str(desc).strip():
        add("D001", BLOCKING, dline, "Missing or empty 'description': Claude can't decide when to use the skill.")
    else:
        desc = " ".join(str(desc).split())
        if len(desc) > DESCRIPTION_MAX:
            add("D002", BLOCKING, dline, f"Description is {len(desc)} characters; maximum is {DESCRIPTION_MAX}.")
        if XML_TAG_RE.search(desc):
            add("D003", BLOCKING, dline, "Description contains an XML tag.")
        when = fm.get("when_to_use")
        combined = len(desc) + (len(" ".join(str(when).split())) + 1 if when else 0)
        if combined > LISTING_ENTRY_MAX:
            add("D004", SHOULD_FIX, dline, f"description + when_to_use is {combined} characters; Claude Code "
                f"truncates the listing at {LISTING_ENTRY_MAX}. Put the key use case first.")
        # Quoted text is usually an example of what users say ("I'm stuck"), not the skill's voice.
        unquoted = QUOTED_RE.sub("", desc)
        if FIRST_PERSON_RE.search(unquoted) or SECOND_PERSON_RE.search(unquoted):
            add("D005", SHOULD_FIX, dline, "Description should be third person ('Processes X…'), "
                "not 'I can…' or 'You can use this…'.")
        if not WHEN_RE.search(desc) and not when:
            add("D006", SHOULD_FIX, dline, "Description doesn't clearly say when to use the skill "
                "(for example, 'Use when …').")

    # Invocation
    dmi, ui = fm.get("disable-model-invocation"), fm.get("user-invocable")
    if isinstance(dmi, str):
        dmi = dmi.lower()
    if isinstance(ui, str):
        ui = ui.lower()
    if dmi in TRUE_VALUES and ui in FALSE_VALUES:
        add("I001", BLOCKING, line_of(text, "user-invocable:"), "disable-model-invocation: true together with "
            "user-invocable: false leaves no way to run the skill.")

    # Body
    body_lines = body.split("\n")
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    if len(body_lines) > BODY_MAX_LINES:
        add("B001", SHOULD_FIX, body_start, f"Body is {len(body_lines)} lines; keep it under {BODY_MAX_LINES} "
            "and move detail into reference files.")
    findings += check_links(skill_md, body, body_start, skill_dir, top_level=True)
    for m in TIME_SENSITIVE_RE.finditer(body):
        add("C007", NIT, body_start + body.count("\n", 0, m.start()),
            f"Time-sensitive wording '{m.group(0)}': will go stale. Use an 'Old patterns' section instead.")
    return findings


def check_links(md_file, text, start_line, skill_dir, top_level):
    findings = []
    in_code = False
    for i, line in enumerate(text.split("\n")):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for m in LINK_RE.finditer(INLINE_CODE_RE.sub("", line)):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#") \
                    or "${" in target or target.startswith("/"):
                continue
            lineno = start_line + i
            if "\\" in target:
                findings.append(Finding("B005", SHOULD_FIX, md_file, lineno,
                                        f"Backslash in path '{target}': use forward slashes."))
                target = target.replace("\\", "/")
            path_part = target.split("#", 1)[0]
            resolved = (md_file.parent / path_part).resolve()
            if not resolved.exists():
                findings.append(Finding("B002", BLOCKING, md_file, lineno, f"Broken link: '{target}' not found."))
                continue
            if top_level and resolved.is_file() and resolved.suffix == ".md":
                findings += check_reference(resolved, skill_dir)
            elif not top_level and resolved.suffix == ".md" and resolved != md_file:
                findings.append(Finding("B003", SHOULD_FIX, md_file, lineno,
                                        f"Nested reference to '{target}': link it directly from SKILL.md "
                                        "instead (keep references one level deep)."))
    return findings


_checked_refs = set()


def check_reference(ref, skill_dir):
    key = (ref, skill_dir)
    if key in _checked_refs:
        return []
    _checked_refs.add(key)
    text = ref.read_text(encoding="utf-8")
    findings = []
    lines = text.rstrip("\n").split("\n")
    if len(lines) > TOC_THRESHOLD_LINES and not TOC_RE.search("\n".join(lines[:TOC_SEARCH_LINES])):
        findings.append(Finding("B004", SHOULD_FIX, ref, 1, f"Reference file is {len(lines)} lines with no "
                                "'Contents' section near the top; add a table of contents."))
    findings += check_links(ref, text, 1, skill_dir, top_level=False)
    return findings


# ---------------------------------------------------------------- driver

def find_skills(path):
    if path.is_file():
        return [path] if path.name == "SKILL.md" else []
    found = []
    for p in sorted(path.rglob("SKILL.md")):
        if not any(part in SKIP_DIRS for part in p.relative_to(path).parts):
            found.append(p)
    return found


def main(argv):
    as_json = "--json" in argv
    paths = [a for a in argv if a != "--json"]
    if not paths:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    skills = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            print(f"error: path not found: {raw}", file=sys.stderr)
            return 2
        skills += find_skills(p.resolve())
    if not skills:
        print("error: no SKILL.md files found under: " + ", ".join(paths), file=sys.stderr)
        return 2

    report = []
    for s in skills:
        report.append({"skill": str(s.parent), "findings": [f.as_dict() for f in check_skill(s)]})
    blocking = sum(1 for r in report for f in r["findings"] if f["severity"] == BLOCKING)

    if as_json:
        print(json.dumps({"yaml_parser": "pyyaml" if yaml else "minimal", "skills": report}, indent=2))
    else:
        icons = {BLOCKING: "🔴", SHOULD_FIX: "🟡", NIT: "⚪"}
        for r in report:
            print(f"\n{r['skill']}")
            if not r["findings"]:
                print("  ✓ no mechanical issues")
            for f in r["findings"]:
                rel = Path(f["file"]).relative_to(r["skill"]) if f["file"].startswith(r["skill"]) else f["file"]
                print(f"  {icons[f['severity']]} {f['rule']} {rel}:{f['line']}  {f['message']}")
        total = sum(len(r["findings"]) for r in report)
        print(f"\n{len(report)} skill(s), {total} finding(s), {blocking} blocking.")
        if yaml is None:
            print("(PyYAML not installed: used the minimal frontmatter parser.)")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
