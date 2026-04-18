#!/usr/bin/env python3
"""
update_tracker.py
-----------------
Scans all Python solution files under solutions/, extracts their YAML metadata
headers, rebuilds tracker/problems.json, and regenerates the README.md
dashboard tables.

Usage:
    python scripts/update_tracker.py

Requirements: Python 3.8+  (stdlib only – no pip install needed)
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS_DIR = REPO_ROOT / "solutions"
TRACKER_FILE = REPO_ROOT / "tracker" / "problems.json"
README_FILE = REPO_ROOT / "README.md"

# ── Metadata field names expected in the YAML-like header ─────────────────────
SCALAR_FIELDS = [
    "id", "title", "url", "difficulty", "status", "hint_level",
    "time_complexity", "space_complexity", "pitfalls",
    "last_reviewed", "next_review", "confidence",
]
LIST_FIELDS = ["companies", "topics"]
MULTILINE_FIELDS = ["key_insight"]

# Markers that delimit the auto-generated README sections
_SEC_START = "<!-- AUTO-GENERATED: {} -->"
_SEC_END   = "<!-- /AUTO-GENERATED: {} -->"

# ── Parser ─────────────────────────────────────────────────────────────────────

def _parse_header(text: str) -> dict[str, Any] | None:
    """
    Extract the YAML-like block between the first ``# ---`` pair in *text*.
    Returns a dict of parsed fields, or None if no header is found.
    """
    lines = text.splitlines()
    in_header = False
    header_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "# ---":
            if not in_header:
                in_header = True
                continue
            else:
                break  # end of header
        if in_header:
            header_lines.append(stripped.lstrip("# ").rstrip())

    if not header_lines:
        return None

    raw_yaml = "\n".join(header_lines)
    return _parse_yaml_subset(raw_yaml)


def _parse_yaml_subset(text: str) -> dict[str, Any]:
    """
    Minimal YAML parser that handles:
      - scalar: key: value
      - lists:  key: [a, b, c]
      - multiline block scalars (key: |\n  line1\n  line2)
    """
    result: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        # key: value  or  key: |
        m = re.match(r'^(\w+):\s*(.*)', line)
        if not m:
            i += 1
            continue

        key, val = m.group(1), m.group(2).strip()

        # Remove inline comment (everything after  # that isn't inside quotes)
        val = re.sub(r'\s+#.*$', '', val).strip()

        if val == "|":
            # Multiline block: collect lines until the next key definition.
            # NOTE: because _parse_header strips leading "# " from every line,
            # YAML indentation is gone – we detect block end by checking whether
            # the next non-blank line looks like a new key (word followed by ':').
            block_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # A new key definition ends the block
                if next_line and re.match(r'^\w+:', next_line):
                    break
                block_lines.append(next_line.strip())
                i += 1
            result[key] = " ".join(bl for bl in block_lines if bl).strip()
            continue

        if val.startswith("[") and val.endswith("]"):
            # Inline list: [a, b, c]
            inner = val[1:-1]
            items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            result[key] = items
        else:
            # Scalar – strip surrounding quotes if any
            val = val.strip('"').strip("'")
            # Try int conversion
            if re.fullmatch(r'\d+', val):
                result[key] = int(val)
            else:
                result[key] = val

        i += 1

    return result


# ── Scanner ────────────────────────────────────────────────────────────────────

def scan_solutions() -> list[dict[str, Any]]:
    """Walk solutions/ and parse metadata from every .py file."""
    problems: list[dict[str, Any]] = []
    if not SOLUTIONS_DIR.exists():
        return problems

    for path in sorted(SOLUTIONS_DIR.glob("lc_*.py")):
        text = path.read_text(encoding="utf-8")
        meta = _parse_header(text)
        if meta is None:
            print(f"  [WARN] No metadata header found in {path.name}", file=sys.stderr)
            continue
        meta["file"] = str(path.relative_to(REPO_ROOT))
        problems.append(meta)

    return problems


# ── Tracker update ─────────────────────────────────────────────────────────────

def update_tracker(problems: list[dict[str, Any]]) -> None:
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(
        json.dumps(problems, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  ✔  tracker/problems.json updated ({len(problems)} problems)")


# ── README generation ──────────────────────────────────────────────────────────

def _replace_section(readme: str, section_name: str, new_content: str) -> str:
    """Replace the content between AUTO-GENERATED markers (or append if absent)."""
    start_tag = _SEC_START.format(section_name)
    end_tag   = _SEC_END.format(section_name)
    pattern   = re.compile(
        re.escape(start_tag) + r".*?" + re.escape(end_tag),
        re.DOTALL,
    )
    replacement = f"{start_tag}\n{new_content}\n{end_tag}"
    if pattern.search(readme):
        return pattern.sub(replacement, readme)
    # Markers not present yet – append to end
    return readme.rstrip() + f"\n\n{replacement}\n"


def _difficulty_emoji(d: str) -> str:
    return {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(d, "⚪")


def _status_emoji(s: str) -> str:
    return {"SOLVED": "✅", "IN_PROGRESS": "🔄", "TODO": "⬜", "REVISIT": "🔁"}.get(s, "❓")


def _hint_emoji(h: str) -> str:
    return {"NONE": "💡", "LIGHT": "🕯️", "HEAVY": "🆘"}.get(h, "")


def _problem_link(p: dict) -> str:
    return f"[{p.get('id', '?')}. {p.get('title', 'Unknown')}]({p.get('url', '#')})"


def build_readme_sections(problems: list[dict[str, Any]]) -> dict[str, str]:
    """Return a dict of section_name → markdown string."""
    sections: dict[str, str] = {}
    today = date.today().isoformat()

    # ── Stats ──────────────────────────────────────────────────────────────────
    total   = len(problems)
    solved  = sum(1 for p in problems if p.get("status") == "SOLVED")
    revisit = sum(1 for p in problems if p.get("status") == "REVISIT")
    todo    = sum(1 for p in problems if p.get("status") == "TODO")
    in_prog = sum(1 for p in problems if p.get("status") == "IN_PROGRESS")

    easy   = sum(1 for p in problems if p.get("difficulty") == "Easy")
    medium = sum(1 for p in problems if p.get("difficulty") == "Medium")
    hard   = sum(1 for p in problems if p.get("difficulty") == "Hard")

    stats_lines = [
        f"> Last updated: **{today}**\n",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total problems | {total} |",
        f"| ✅ Solved | {solved} |",
        f"| 🔁 Revisit | {revisit} |",
        f"| 🔄 In Progress | {in_prog} |",
        f"| ⬜ TODO | {todo} |",
        f"| 🟢 Easy | {easy} |",
        f"| 🟡 Medium | {medium} |",
        f"| 🔴 Hard | {hard} |",
    ]
    sections["STATS"] = "\n".join(stats_lines)

    # ── All problems table ─────────────────────────────────────────────────────
    rows = [
        "| # | Title | Difficulty | Topics | Companies | Status | Hint | Confidence | File |",
        "|---|-------|------------|--------|-----------|--------|------|------------|------|",
    ]
    for p in sorted(problems, key=lambda x: int(x.get("id", 0))):
        row = (
            f"| {p.get('id', '')} "
            f"| {_problem_link(p)} "
            f"| {_difficulty_emoji(p.get('difficulty',''))} {p.get('difficulty','')} "
            f"| {', '.join(p.get('topics', []))} "
            f"| {', '.join(p.get('companies', []))} "
            f"| {_status_emoji(p.get('status',''))} {p.get('status','')} "
            f"| {_hint_emoji(p.get('hint_level',''))} {p.get('hint_level','')} "
            f"| {'⭐' * int(p.get('confidence', 0))} "
            f"| [{p.get('file','').split('/')[-1]}]({p.get('file','#')}) |"
        )
        rows.append(row)
    sections["ALL_PROBLEMS"] = "\n".join(rows)

    # ── Revisit queue ──────────────────────────────────────────────────────────
    revisit_problems = [p for p in problems if p.get("status") in ("REVISIT", "IN_PROGRESS")]
    if revisit_problems:
        rev_rows = [
            "| # | Title | Difficulty | Hint | Next Review | Confidence |",
            "|---|-------|------------|------|-------------|------------|",
        ]
        for p in sorted(revisit_problems, key=lambda x: x.get("next_review", "9999")):
            rev_rows.append(
                f"| {p.get('id','')} "
                f"| {_problem_link(p)} "
                f"| {_difficulty_emoji(p.get('difficulty',''))} {p.get('difficulty','')} "
                f"| {_hint_emoji(p.get('hint_level',''))} {p.get('hint_level','')} "
                f"| {p.get('next_review', '-')} "
                f"| {'⭐' * int(p.get('confidence', 0))} |"
            )
        sections["REVISIT_QUEUE"] = "\n".join(rev_rows)
    else:
        sections["REVISIT_QUEUE"] = "_No problems in revisit queue right now. 🎉_"

    # ── Per-topic breakdown ────────────────────────────────────────────────────
    topic_map: dict[str, list[dict]] = {}
    for p in problems:
        for t in p.get("topics", []):
            topic_map.setdefault(t, []).append(p)

    topic_rows = [
        "| Topic | Total | Solved | Revisit | TODO |",
        "|-------|-------|--------|---------|------|",
    ]
    for topic in sorted(topic_map):
        ps = topic_map[topic]
        topic_rows.append(
            f"| {topic} "
            f"| {len(ps)} "
            f"| {sum(1 for p in ps if p.get('status')=='SOLVED')} "
            f"| {sum(1 for p in ps if p.get('status')=='REVISIT')} "
            f"| {sum(1 for p in ps if p.get('status')=='TODO')} |"
        )
    sections["TOPIC_BREAKDOWN"] = "\n".join(topic_rows)

    # ── Per-company breakdown ─────────────────────────────────────────────────
    company_map: dict[str, list[dict]] = {}
    for p in problems:
        for c in p.get("companies", []):
            company_map.setdefault(c, []).append(p)

    company_rows = [
        "| Company | Total | Solved | Revisit | TODO |",
        "|---------|-------|--------|---------|------|",
    ]
    for company in sorted(company_map):
        ps = company_map[company]
        company_rows.append(
            f"| {company} "
            f"| {len(ps)} "
            f"| {sum(1 for p in ps if p.get('status')=='SOLVED')} "
            f"| {sum(1 for p in ps if p.get('status')=='REVISIT')} "
            f"| {sum(1 for p in ps if p.get('status')=='TODO')} |"
        )
    sections["COMPANY_BREAKDOWN"] = "\n".join(company_rows)

    return sections


def update_readme(problems: list[dict[str, Any]]) -> None:
    readme_text = README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else ""
    sections = build_readme_sections(problems)
    for name, content in sections.items():
        readme_text = _replace_section(readme_text, name, content)
    README_FILE.write_text(readme_text, encoding="utf-8")
    print("  ✔  README.md dashboard updated")


# ── Company & topic index pages ────────────────────────────────────────────────

def update_company_indexes(problems: list[dict[str, Any]]) -> None:
    company_dir = REPO_ROOT / "company"
    company_dir.mkdir(exist_ok=True)

    company_map: dict[str, list[dict]] = {}
    for p in problems:
        for c in p.get("companies", []):
            company_map.setdefault(c, []).append(p)

    for company, ps in company_map.items():
        slug = company.lower().replace(" ", "_")
        lines = [
            f"# {company} – LeetCode Problems\n",
            f"| # | Title | Difficulty | Topics | Status | File |",
            f"|---|-------|------------|--------|--------|------|",
        ]
        for p in sorted(ps, key=lambda x: int(x.get("id", 0))):
            lines.append(
                f"| {p.get('id','')} "
                f"| {_problem_link(p)} "
                f"| {_difficulty_emoji(p.get('difficulty',''))} {p.get('difficulty','')} "
                f"| {', '.join(p.get('topics', []))} "
                f"| {_status_emoji(p.get('status',''))} {p.get('status','')} "
                f"| [{p.get('file','').split('/')[-1]}](../{p.get('file','#')}) |"
            )
        out = company_dir / f"{slug}.md"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✔  company/ index pages updated ({len(company_map)} companies)")


def update_topic_indexes(problems: list[dict[str, Any]]) -> None:
    topic_dir = REPO_ROOT / "topics"
    topic_dir.mkdir(exist_ok=True)

    topic_map: dict[str, list[dict]] = {}
    for p in problems:
        for t in p.get("topics", []):
            topic_map.setdefault(t, []).append(p)

    for topic, ps in topic_map.items():
        slug = topic.lower().replace(" ", "_")
        lines = [
            f"# {topic} – LeetCode Problems\n",
            f"| # | Title | Difficulty | Companies | Status | File |",
            f"|---|-------|------------|-----------|--------|------|",
        ]
        for p in sorted(ps, key=lambda x: int(x.get("id", 0))):
            lines.append(
                f"| {p.get('id','')} "
                f"| {_problem_link(p)} "
                f"| {_difficulty_emoji(p.get('difficulty',''))} {p.get('difficulty','')} "
                f"| {', '.join(p.get('companies', []))} "
                f"| {_status_emoji(p.get('status',''))} {p.get('status','')} "
                f"| [{p.get('file','').split('/')[-1]}](../{p.get('file','#')}) |"
            )
        out = topic_dir / f"{slug}.md"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✔  topics/ index pages updated ({len(topic_map)} topics)")


# ── CLI query helper ───────────────────────────────────────────────────────────

def query_problems(problems: list[dict], args: list[str]) -> None:
    """
    Simple CLI filter:
        --status REVISIT
        --difficulty Medium
        --topic DP
        --company Amazon
    Flags can be combined (AND logic).
    """
    filtered = problems
    i = 0
    while i < len(args):
        flag = args[i]
        if i + 1 >= len(args):
            break
        value = args[i + 1].lower()
        i += 2
        if flag == "--status":
            filtered = [p for p in filtered if p.get("status", "").lower() == value]
        elif flag == "--difficulty":
            filtered = [p for p in filtered if p.get("difficulty", "").lower() == value]
        elif flag == "--topic":
            filtered = [p for p in filtered if any(value in t.lower() for t in p.get("topics", []))]
        elif flag == "--company":
            filtered = [p for p in filtered if any(value in c.lower() for c in p.get("companies", []))]

    if not filtered:
        print("No problems match the given filters.")
        return

    print(f"{'ID':<6} {'Title':<50} {'Diff':<8} {'Status':<12} {'Hint':<8}")
    print("-" * 86)
    for p in sorted(filtered, key=lambda x: int(x.get("id", 0))):
        print(
            f"{p.get('id',''):<6} "
            f"{p.get('title','')[:48]:<50} "
            f"{p.get('difficulty',''):<8} "
            f"{p.get('status',''):<12} "
            f"{p.get('hint_level',''):<8}"
        )


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan solutions and update tracker + README dashboard."
    )
    parser.add_argument(
        "--query", action="store_true",
        help="Run a query instead of updating files. Pass --status/--difficulty/--topic/--company."
    )
    parser.add_argument("--status",     help="Filter by status (SOLVED/REVISIT/TODO/IN_PROGRESS)")
    parser.add_argument("--difficulty", help="Filter by difficulty (Easy/Medium/Hard)")
    parser.add_argument("--topic",      help="Filter by topic (substring match)")
    parser.add_argument("--company",    help="Filter by company (substring match)")
    args = parser.parse_args()

    print("🔍  Scanning solutions/ …")
    problems = scan_solutions()
    print(f"   Found {len(problems)} solution file(s).")

    if args.query:
        query_args = []
        if args.status:
            query_args += ["--status", args.status]
        if args.difficulty:
            query_args += ["--difficulty", args.difficulty]
        if args.topic:
            query_args += ["--topic", args.topic]
        if args.company:
            query_args += ["--company", args.company]
        query_problems(problems, query_args)
        return

    print("📝  Updating tracker …")
    update_tracker(problems)

    print("📊  Rebuilding README dashboard …")
    update_readme(problems)

    print("🏢  Updating company index pages …")
    update_company_indexes(problems)

    print("🗂️   Updating topic index pages …")
    update_topic_indexes(problems)

    print("\n✅  Done!  Commit tracker/problems.json, README.md, company/, topics/ to persist.")


if __name__ == "__main__":
    main()
