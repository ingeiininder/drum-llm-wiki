import os
import re
import argparse
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
SEARCH_PATHS = [
    WIKI_DIR / "topics",
    WIKI_DIR / "exercises",
    WIKI_DIR / "entities"
]

def search_wiki(query, case_insensitive=True):
    print(f"[*] Searching for: '{query}'...")
    
    # Compile regex for speed
    flags = re.IGNORECASE if case_insensitive else 0
    try:
        pattern = re.compile(query, flags)
    except re.error:
        print(f"[!] Invalid regex pattern: {query}. Falling back to literal search.")
        pattern = re.compile(re.escape(query), flags)

    matches = []
    
    for path in SEARCH_PATHS:
        if not path.exists():
            continue
            
        for filepath in sorted(path.glob("*.md")):
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                
                # Check filename or content
                if pattern.search(filepath.name) or pattern.search(content):
                    # Extract title from frontmatter or first H1
                    title_match = re.search(r"^title:\s*(.+)", content, re.MULTILINE)
                    if not title_match:
                        title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
                    
                    title = title_match.group(1).strip() if title_match else filepath.stem
                    
                    # Simple summary extraction
                    body = re.sub(r"^---.*?---\s*", "", content, flags=re.DOTALL)
                    body = re.sub(r"^#+.+$", "", body, flags=re.MULTILINE).strip()
                    summary = ""
                    if body:
                        # Get first line that isn't empty
                        lines = [l.strip() for l in body.split('\n') if l.strip()]
                        summary = lines[0][:100] if lines else ""
                    
                    matches.append({
                        "file": filepath.name,
                        "title": title,
                        "summary": summary,
                        "path": filepath.relative_to(ROOT_DIR)
                    })
            except Exception as e:
                print(f"[!] Error reading {filepath}: {e}")

    if not matches:
        print("[-] No matches found.")
    else:
        print(f"[V] Found {len(matches)} matches:\n")
        for m in matches:
            print(f"- [[{m['file']}]] — {m['title']}")
            if m['summary']:
                print(f"  Summary: {m['summary']}...")
            print(f"  Path: {m['path']}")
            print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Search CLI Tool")
    parser.add_argument("query", type=str, help="Search query (supports Regex)")
    parser.add_argument("-i", "--insensitive", action="store_false", help="Case sensitive search")
    
    args = parser.parse_args()
    search_wiki(args.query, args.insensitive)
