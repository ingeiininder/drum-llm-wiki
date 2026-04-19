"""
fix_links.py — Groove Hub Wiki Broken Link Fixer
Automatically repairs [[wikilinks]] that don't match actual node filenames.
Strategy: normalize both link target and node stems, find best match, rewrite in-place.
No API key required.

Safe by design:
- Only rewrites links that are currently broken (target file doesn't exist)
- Never deletes or moves files
- Writes a fix_report.md showing every change made
- Dry-run mode available (--dry-run)
"""

import re
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import date
from difflib import get_close_matches

ROOT_DIR = Path(__file__).parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
TOPICS_DIR = WIKI_DIR / "topics"
EXERCISES_DIR = WIKI_DIR / "exercises"
ENTITIES_DIR = WIKI_DIR / "entities"
FIX_REPORT_PATH = WIKI_DIR / "fix_report.md"

ALL_CATEGORY_DIRS = [TOPICS_DIR, EXERCISES_DIR, ENTITIES_DIR]


def get_all_nodes() -> dict[str, Path]:
    """Return {stem: filepath} for all wiki nodes."""
    nodes = {}
    for d in ALL_CATEGORY_DIRS:
        for f in d.glob("*.md"):
            nodes[f.stem] = f
    return nodes


def normalize(s: str) -> str:
    """
    Normalize a stem or link target for fuzzy matching.
    Strips spaces, underscores, hyphens, brackets, lowercases, removes trailing 's'.
    """
    s = s.strip()
    s = re.sub(r"[\[\]]", "", s)          # remove brackets
    s = re.sub(r"[_\-\s]+", "", s)        # remove separators
    s = s.lower()
    if s.endswith("s") and len(s) > 3:
        s = s[:-1]                         # basic depluralization
    return s


def build_lookup(all_nodes: dict[str, Path]) -> dict[str, str]:
    """
    Build {normalized_stem: original_stem} lookup table.
    When there are collisions, prefer shorter stem.
    """
    lookup = {}
    for stem in all_nodes:
        norm = normalize(stem)
        if norm not in lookup:
            lookup[norm] = stem
        else:
            # Prefer shorter (less specific) name
            if len(stem) < len(lookup[norm]):
                lookup[norm] = stem
    return lookup


def find_best_match(target: str, lookup: dict[str, str], all_stems: list[str]) -> str | None:
    """
    Try to find the best matching node stem for a broken link target.
    Returns the correct stem, or None if no confident match found.
    """
    # 1. Try direct underscore/space normalization first
    target_underscore = target.strip().replace(" ", "_")
    if target_underscore in all_stems:
        return target_underscore

    # 2. Try normalized lookup
    norm_target = normalize(target)
    if norm_target in lookup:
        return lookup[norm_target]

    # 3. Try fuzzy match on normalized stems (high cutoff for safety)
    norm_stems = list(lookup.keys())
    close = get_close_matches(norm_target, norm_stems, n=1, cutoff=0.90)
    if close:
        return lookup[close[0]]

    return None


def extract_wikilinks_with_positions(text: str):
    """
    Extract all [[...]] wikilinks with their spans.
    Returns list of (start, end, raw_match, link_target, display_text)
    """
    results = []
    for m in re.finditer(r'\[\[([^\]]+?)\]\]', text):
        content = m.group(1)
        if "|" in content:
            target, display = content.split("|", 1)
        else:
            target, display = content, None
        results.append((m.start(), m.end(), m.group(0), target.strip(), display))
    return results


def fix_file(fpath: Path, all_nodes: dict[str, Path],
             lookup: dict[str, str], all_stems: list[str],
             dry_run: bool) -> list[tuple[str, str]]:
    """
    Fix broken wikilinks in a single file.
    Returns list of (original_link, replacement_link) changes made.
    """
    text = fpath.read_text(encoding="utf-8", errors="ignore")
    changes = []
    new_text = text

    links = extract_wikilinks_with_positions(text)
    # Process in reverse order so span indices stay valid
    for start, end, raw, target, display in reversed(links):
        # Skip frontmatter
        if start < text.find("---\n", 3) + 4:
            continue

        # Normalize target to underscore format for existence check
        target_norm = target.replace(" ", "_")

        # Skip if link already resolves correctly
        if target_norm in all_nodes or target in all_nodes:
            continue

        # Try to find a match
        best = find_best_match(target, lookup, all_stems)
        if best is None:
            continue

        # Build replacement link
        if display:
            replacement = f"[[{best}|{display}]]"
        else:
            replacement = f"[[{best}]]"

        if replacement != raw:
            changes.append((raw, replacement))
            new_text = new_text[:start] + replacement + new_text[end:]

    if changes and not dry_run:
        fpath.write_text(new_text, encoding="utf-8")

    return changes


def run_fix(dry_run: bool = False):
    today = date.today().isoformat()
    all_nodes = get_all_nodes()
    all_stems = list(all_nodes.keys())
    lookup = build_lookup(all_nodes)

    print(f"[*] Fixing broken links across {len(all_nodes)} nodes...")
    if dry_run:
        print("    [DRY RUN MODE — no files will be modified]")

    total_fixes = 0
    total_unfixable = 0
    file_fix_log: list[tuple[str, list[tuple[str, str]]]] = []
    unfixable_log: dict[str, int] = defaultdict(int)

    for stem, fpath in all_nodes.items():
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        links = extract_wikilinks_with_positions(text)
        broken_in_file = []

        for start, end, raw, target, display in links:
            target_norm = target.replace(" ", "_")
            if target_norm not in all_nodes and target not in all_nodes:
                best = find_best_match(target, lookup, all_stems)
                if best is None:
                    unfixable_log[target] += 1
                    total_unfixable += 1

        changes = fix_file(fpath, all_nodes, lookup, all_stems, dry_run)
        if changes:
            file_fix_log.append((stem, changes))
            total_fixes += len(changes)
            print(f"    [+] {stem}: {len(changes)} links fixed")

    print(f"\n{'='*60}")
    print(f"  FIX RESULTS — {today}")
    print(f"{'='*60}")
    print(f"  Files modified:    {len(file_fix_log)}")
    print(f"  Total links fixed: {total_fixes}")
    print(f"  Still unfixable:   {total_unfixable} unique broken targets")
    if dry_run:
        print("  [DRY RUN — no changes written to disk]")
    print(f"{'='*60}\n")

    # Write fix report
    lines = []
    lines.append("---")
    lines.append("type: fix-report")
    lines.append(f"date: {today}")
    lines.append(f"total_fixes: {total_fixes}")
    lines.append(f"files_modified: {len(file_fix_log)}")
    lines.append("---")
    lines.append("")
    lines.append("# Groove Hub Wiki Fix Report")
    lines.append("")
    lines.append(f"Generated: {today}  |  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Files modified | {len(file_fix_log)} |")
    lines.append(f"| Total links fixed | {total_fixes} |")
    lines.append(f"| Unfixable broken links | {total_unfixable} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Top 30 Unfixable Targets (manual review needed)")
    lines.append("")
    lines.append("These link targets could not be matched to any existing node.")
    lines.append("Consider creating new nodes or deleting these references.")
    lines.append("")
    top_unfixable = sorted(unfixable_log.items(), key=lambda x: -x[1])[:30]
    for target, count in top_unfixable:
        lines.append(f"- `[[{target}]]` — referenced {count}x")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## Files Modified ({len(file_fix_log)})")
    lines.append("")
    for stem, changes in file_fix_log[:100]:
        lines.append(f"### {stem}")
        for orig, repl in changes[:10]:
            lines.append(f"  - `{orig}` → `{repl}`")
        if len(changes) > 10:
            lines.append(f"  - ... and {len(changes) - 10} more")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by `pipeline/fix_links.py` — re-run lint_wiki.py to verify improvement.*")

    FIX_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[V] Fix report written to: {FIX_REPORT_PATH}")

    return total_fixes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Groove Hub Wiki Broken Link Fixer")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without modifying any files")
    args = parser.parse_args()
    run_fix(dry_run=args.dry_run)
