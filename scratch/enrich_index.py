import os
import re

def enrich_index(wiki_dir):
    topics_dir = os.path.join(wiki_dir, 'topics')
    all_files = sorted([f for f in os.listdir(topics_dir) if f.endswith('.md')])
    
    categories = {
        "Musical Styles": [],
        "Techniques & Articulations": [],
        "Music Theory & Notation": [],
        "Rudiments": [],
        "Coordination & Independence": [],
        "Instruments & Gear": [],
        "Song Studies & Performances": [],
        "General Concepts": []
    }
    
    def get_summary(content):
        # 1. Remove Frontmatter
        text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        # 2. Remove H1 Title
        text = re.sub(r'^#\s+.*?\n', '', text).strip()
        # 3. Handle cases where the first thing is a Bold term or a link
        # Extract the first sentence or first 100 characters
        # Try to find the first paragraph
        paragraphs = [p for p in text.split('\n') if p.strip() and not p.strip().startswith('!') and not p.strip().startswith('[')]
        if not paragraphs:
            return "No summary available."
        
        first_p = paragraphs[0]
        # Clean internal links [[A|B]] -> B or [[A]] -> A
        clean_p = re.sub(r'\[\[(?:.*?\|)?(.*?)\]\]', r'\1', first_p)
        
        # Take the first sentence (roughly)
        sentence_match = re.search(r'^(.*?[。\.!\?])', clean_p)
        if sentence_match:
            summary = sentence_match.group(1).strip()
        else:
            summary = clean_p[:120].strip() + ("..." if len(clean_p) > 120 else "")
            
        return summary

    for f in all_files:
        if f == "Topics_Index.md": continue
        
        path = os.path.join(topics_dir, f)
        basename = f[:-3]
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        summary = get_summary(content)
        
        # Heuristic Categorization (Same logic as generate_topics_index but simplified)
        lower_name = basename.lower()
        lower_content = content.lower()
        
        entry = (basename, summary)
        
        if any(s in lower_name for s in ["rock", "blues", "funk", "jazz", "pop", "reggae", "bossa", "samba", "cumbia"]):
            categories["Musical Styles"].append(entry)
        elif any(r in lower_name for r in ["paradiddle", "roll", "flam", "drag", "ruff", "stroke_roll", "diddle", "herta"]):
            categories["Rudiments"].append(entry)
        elif any(t in lower_name for t in ["time_signature", "note", "rest", "meter", "measure", "clef", "tempo", "dynamics", "staccato"]):
            categories["Music Theory & Notation"].append(entry)
        elif any(t in lower_name for t in ["stroke", "grip", "articulation", "hand", "foot", "wrist", "heel", "ankle", "fulcrum"]):
            categories["Techniques & Articulations"].append(entry)
        elif any(i in lower_name for i in ["bass_drum", "snare", "hi-hat", "ride", "tom", "cymbal", "beater", "kit", "seat"]):
            categories["Instruments & Gear"].append(entry)
        elif "unit" in lower_name or "study" in lower_name or "IMG_" in lower_content:
            categories["Song Studies & Performances"].append(entry)
        else:
            categories["General Concepts"].append(entry)

    # Build the enriched Topics_Index.md
    index_content = "---\ntype: index\ntitle: 全域主題索引 (Enriched Topics Index)\nlast_updated: 2026-04-20\n---\n\n"
    index_content += "# 全域主題索引 (Enriched Topics Index)\n\n"
    index_content += "**Karpathy Pattern**: 此索引為全庫節點提供「連結 + 一行摘要」，以便於 AI 代理快速檢索與語義導解。\n\n"
    
    for cat, items in categories.items():
        if not items: continue
        index_content += f"## {cat}\n"
        # Sort items
        sorted_items = sorted(items, key=lambda x: x[0])
        for name, summ in sorted_items:
            index_content += f"- [[{name}|{name.replace('_', ' ')}]] — {summ}\n"
        index_content += "\n"

    index_path = os.path.join(topics_dir, 'Topics_Index.md')
    with open(index_path, 'w', encoding='utf-8') as file:
        file.write(index_content)
    
    print(f"Generated Enriched Index for {sum(len(v) for v in categories.values())} files.")

if __name__ == "__main__":
    enrich_index('c:/Users/USER/.gemini/antigravity/scratch/drum-llm-wiki/wiki')
