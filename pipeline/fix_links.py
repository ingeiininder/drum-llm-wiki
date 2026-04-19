import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
TOPICS_DIR = WIKI_DIR / "topics"
EXERCISES_DIR = WIKI_DIR / "exercises"
ENTITIES_DIR = WIKI_DIR / "entities"

ALL_DIRS = [TOPICS_DIR, EXERCISES_DIR, ENTITIES_DIR]

def get_all_nodes():
    nodes = {} # stem -> display_name (original stem)
    normalized_map = {} # normalized -> display_name
    for d in ALL_DIRS:
        if not d.exists(): continue
        for f in d.glob("*.md"):
            stem = f.stem
            nodes[stem] = stem
            normalized_map[stem.lower().replace(" ", "_").replace("-", "_")] = stem
    return nodes, normalized_map

def fix_links():
    nodes, norm_map = get_all_nodes()
    print(f"[*] Loaded {len(nodes)} nodes.")

    fix_count = 0
    file_count = 0

    for d in ALL_DIRS:
        if not d.exists(): continue
        for fpath in d.glob("*.md"):
            file_count += 1
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            
            def replace_link(match):
                nonlocal fix_count
                link_text = match.group(1)
                # Split by | for display text
                parts = link_text.split('|', 1)
                target = parts[0].strip()
                display = parts[1] if len(parts) > 1 else None

                # Normalize target
                target_norm = target.replace(" ", "_")
                
                # If target_norm exists as-is, return (standardize underscores)
                if target_norm in nodes:
                    if target != target_norm:
                        fix_count += 1
                        return f"[[{target_norm}" + (f"|{display}]]" if display else "]]")
                    return match.group(0)

                # Try fuzzy match (case insensitive, space/hyphen/underscore insensitive)
                fuzzy_key = target.lower().replace(" ", "_").replace("-", "_")
                if fuzzy_key in norm_map:
                    matched_stem = norm_map[fuzzy_key]
                    fix_count += 1
                    return f"[[{matched_stem}" + (f"|{display}]]" if display else "]]")

                # No match found
                return match.group(0)

            new_content = re.sub(r'\[\[([^\]]+)\]\]', replace_link, content)
            
            if new_content != content:
                fpath.write_text(new_content, encoding="utf-8")

    print(f"[V] Link repair complete.")
    print(f"    Processed {file_count} files.")
    print(f"    Fixed {fix_count} links.")

if __name__ == "__main__":
    fix_links()
