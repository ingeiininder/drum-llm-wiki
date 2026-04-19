"""
lint_wiki.py — Groove Hub Wiki Health Check (Structural Lint)
Checks for: orphan nodes, broken links, thin content, missing frontmatter, near-duplicates.
No API key required.
"""

import re
from pathlib import Path
from collections import defaultdict
from datetime import date

ROOT_DIR = Path(__file__).parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
TOPICS_DIR = WIKI_DIR / "topics"
EXERCISES_DIR = WIKI_DIR / "exercises"
ENTITIES_DIR = WIKI_DIR / "entities"
REPORT_PATH = WIKI_DIR / "lint_report.md"

ALL_CATEGORY_DIRS = [TOPICS_DIR, EXERCISES_DIR, ENTITIES_DIR]
REQUIRED_FRONTMATTER = ["type", "source", "tags", "last_updated"]
THIN_NODE_THRESHOLD = 15   # lines
FEW_LINKS_THRESHOLD = 1    # outbound [[]] links


def get_all_nodes() -> dict[str, Path]:
    """Return {stem: filepath} for all wiki nodes."""
    nodes = {}
    for d in ALL_CATEGORY_DIRS:
        for f in d.glob("*.md"):
            nodes[f.stem] = f
    return nodes


def extract_wikilinks(text: str) -> list[str]:
    """Extract all [[Target]] link targets from text."""
    return re.findall(r'\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]', text)


def parse_frontmatter_fields(text: str) -> set[str]:
    """Return set of frontmatter field names present in the file."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return set()
    fields = set()
    for line in match.group(1).splitlines():
        if ":" in line:
            key = line.split(":")[0].strip()
            if key:
                fields.add(key)
    return fields


def get_line_count(text: str) -> int:
    """Count non-empty, non-frontmatter lines."""
    # Strip frontmatter
    body = re.sub(r"^---.*?---\s*\n", "", text, flags=re.DOTALL)
    return sum(1 for line in body.splitlines() if line.strip())


def normalize(stem: str) -> str:
    """Normalize a stem for fuzzy duplicate detection."""
    return re.sub(r"[_\-\s]", "", stem).lower()


def run_lint():
    today = date.today().isoformat()
    all_nodes = get_all_nodes()
    total = len(all_nodes)

    print(f"[*] Starting lint on {total} wiki nodes...")

    # ------------------------------------------------------------------ #
    # Pass 1: Read all files, extract links + metadata
    # ------------------------------------------------------------------ #
    outbound_links: dict[str, list[str]] = {}  # stem -> [linked stems]
    inbound_count: dict[str, int] = defaultdict(int)
    thin_nodes: list[tuple[str, int]] = []
    missing_frontmatter: list[tuple[str, list[str]]] = []
    no_frontmatter: list[str] = []
    file_texts: dict[str, str] = {}

    for stem, fpath in all_nodes.items():
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        file_texts[stem] = text

        links = extract_wikilinks(text)
        # Normalize link targets to stems (replace spaces with underscores)
        normalized_links = [l.strip().replace(" ", "_") for l in links]
        outbound_links[stem] = normalized_links

        for target in normalized_links:
            inbound_count[target] += 1

        # Check content depth
        line_count = get_line_count(text)
        if line_count < THIN_NODE_THRESHOLD:
            thin_nodes.append((stem, line_count))

        # Check frontmatter
        fields = parse_frontmatter_fields(text)
        if not fields:
            no_frontmatter.append(stem)
        else:
            missing = [f for f in REQUIRED_FRONTMATTER if f not in fields]
            if missing:
                missing_frontmatter.append((stem, missing))

    # ------------------------------------------------------------------ #
    # Pass 2: Derive issues
    # ------------------------------------------------------------------ #

    # Orphan nodes: no inbound links from any other wiki node
    orphans = [stem for stem in all_nodes if inbound_count.get(stem, 0) == 0]
    orphans.sort()

    # Isolated nodes: very few outbound links
    isolated = [(stem, len(links))
                for stem, links in outbound_links.items()
                if len(links) <= FEW_LINKS_THRESHOLD]
    isolated.sort(key=lambda x: x[1])

    # Broken links: [[Target]] references that don't exist as nodes
    broken_links: list[tuple[str, str]] = []
    for stem, links in outbound_links.items():
        for target in links:
            if target not in all_nodes:
                broken_links.append((stem, target))

    # Near-duplicate detection: stems that normalize to the same string
    norm_map: dict[str, list[str]] = defaultdict(list)
    for stem in all_nodes:
        norm_map[normalize(stem)].append(stem)
    duplicates = {k: v for k, v in norm_map.items() if len(v) > 1}

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    print(f"\n{'='*60}")
    print(f"  LINT RESULTS — {today}")
    print(f"{'='*60}")
    print(f"  Total nodes:           {total}")
    print(f"  Orphan nodes:          {len(orphans)}")
    print(f"  Isolated nodes (~0 outbound links): {len(isolated)}")
    print(f"  Broken [[links]]:      {len(broken_links)}")
    print(f"  Thin nodes (<{THIN_NODE_THRESHOLD} lines): {len(thin_nodes)}")
    print(f"  Missing frontmatter:   {len(no_frontmatter)}")
    print(f"  Incomplete frontmatter:{len(missing_frontmatter)}")
    print(f"  Near-duplicates:       {len(duplicates)}")
    print(f"{'='*60}\n")

    # ------------------------------------------------------------------ #
    # Write lint_report.md
    # ------------------------------------------------------------------ #
    lines = []
    lines.append("---")
    lines.append("type: lint-report")
    lines.append(f"date: {today}")
    lines.append(f"total_nodes: {total}")
    lines.append("---")
    lines.append("")
    lines.append("# Groove Hub Wiki Lint Report")
    lines.append("")
    lines.append(f"Generated: {today}  |  Total nodes scanned: **{total}**")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("| Issue | Count | Severity |")
    lines.append("|-------|-------|----------|")
    lines.append(f"| Orphan nodes (no inbound links) | {len(orphans)} | High |")
    lines.append(f"| Isolated nodes (<=1 outbound link) | {len(isolated)} | Medium |")
    lines.append(f"| Broken [[links]] | {len(broken_links)} | High |")
    lines.append(f"| Thin nodes (<{THIN_NODE_THRESHOLD} lines) | {len(thin_nodes)} | Medium |")
    lines.append(f"| Missing frontmatter entirely | {len(no_frontmatter)} | High |")
    lines.append(f"| Incomplete frontmatter | {len(missing_frontmatter)} | Medium |")
    lines.append(f"| Near-duplicate node names | {len(duplicates)} | Medium |")
    lines.append("")
    lines.append("---")

    # Orphans
    lines.append("")
    lines.append(f"## 1. Orphan Nodes ({len(orphans)} — no inbound links)")
    lines.append("")
    lines.append("These nodes are not referenced by any other node. Risk: inaccessible to LLM navigation.")
    lines.append("")
    for s in orphans[:100]:
        cat = "topics" if (TOPICS_DIR / f"{s}.md").exists() else \
              "exercises" if (EXERCISES_DIR / f"{s}.md").exists() else "entities"
        lines.append(f"- [[{s}]] `{cat}`")
    if len(orphans) > 100:
        lines.append(f"- ... and {len(orphans) - 100} more (see full scan)")
    lines.append("")
    lines.append("---")

    # Broken links
    lines.append("")
    lines.append(f"## 2. Broken [[Links]] ({len(broken_links)} — target node does not exist)")
    lines.append("")
    for src, tgt in broken_links[:60]:
        lines.append(f"- [[{src}]] links to `[[{tgt}]]` (missing)")
    if len(broken_links) > 60:
        lines.append(f"- ... and {len(broken_links) - 60} more")
    lines.append("")
    lines.append("---")

    # Thin nodes
    lines.append("")
    lines.append(f"## 3. Thin Nodes (<{THIN_NODE_THRESHOLD} lines, {len(thin_nodes)} total)")
    lines.append("")
    lines.append("These nodes may lack sufficient content for useful LLM retrieval.")
    lines.append("")
    for s, lc in sorted(thin_nodes, key=lambda x: x[1])[:60]:
        cat = "topics" if (TOPICS_DIR / f"{s}.md").exists() else \
              "exercises" if (EXERCISES_DIR / f"{s}.md").exists() else "entities"
        lines.append(f"- [[{s}]] — {lc} lines `{cat}`")
    lines.append("")
    lines.append("---")

    # Missing frontmatter
    lines.append("")
    lines.append(f"## 4. Missing/Incomplete Frontmatter ({len(no_frontmatter) + len(missing_frontmatter)} total)")
    lines.append("")
    if no_frontmatter:
        lines.append("### No frontmatter at all:")
        for s in no_frontmatter[:30]:
            lines.append(f"- [[{s}]]")
    if missing_frontmatter:
        lines.append("")
        lines.append("### Missing required fields:")
        for s, fields in missing_frontmatter[:40]:
            lines.append(f"- [[{s}]] — missing: `{', '.join(fields)}`")
    lines.append("")
    lines.append("---")

    # Near-duplicates
    lines.append("")
    lines.append(f"## 5. Near-Duplicate Node Names ({len(duplicates)} groups)")
    lines.append("")
    lines.append("These pairs may represent the same concept split across multiple files.")
    lines.append("")
    for norm_key, stems in list(duplicates.items())[:40]:
        lines.append(f"- `{norm_key}` → " + " | ".join(f"[[{s}]]" for s in stems))
    lines.append("")
    lines.append("---")

    # Hub nodes (most inbound links — useful context)
    hub_nodes = sorted(inbound_count.items(), key=lambda x: x[1], reverse=True)[:20]
    lines.append("")
    lines.append("## 6. Top Hub Nodes (Most Inbound Links)")
    lines.append("")
    lines.append("Highest connectivity nodes — these are the knowledge backbone.")
    lines.append("")
    for stem, cnt in hub_nodes:
        lines.append(f"- [[{stem}]] — {cnt} inbound links")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `pipeline/lint_wiki.py` — re-run periodically to track wiki health.*")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[V] Lint report written to: {REPORT_PATH}")
    print(f"    Size: {REPORT_PATH.stat().st_size / 1024:.1f} KB")

    return {
        "orphans": len(orphans),
        "broken_links": len(broken_links),
        "thin_nodes": len(thin_nodes),
        "duplicates": len(duplicates),
    }


if __name__ == "__main__":
    run_lint()
