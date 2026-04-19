import os
import re

def generate_topics_index(wiki_dir):
    topics_dir = os.path.join(wiki_dir, 'topics')
    all_files = [f for f in os.listdir(topics_dir) if f.endswith('.md')]
    
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
    
    for f in all_files:
        path = os.path.join(topics_dir, f)
        basename = f[:-3]
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Regex to find tags and type in frontmatter
        tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
        type_match = re.search(r'type:\s*(.*)', content)
        
        tags = []
        if tags_match:
            tags_str = tags_match.group(1)
            # Split and clean
            tags = [t.strip().replace('[[', '').replace(']]', '') for t in tags_str.split(',') if t.strip()]
            
        node_type = type_match.group(1).strip() if type_match else "topic"
        
        # Heuristic Categorization
        categorized = False
        
        lower_name = basename.lower()
        lower_content = content.lower()
        
        # Styles
        if "style" in tags or "drumming" in tags or any(s in lower_name for s in ["rock", "blues", "funk", "jazz", "pop", "reggae", "bossa", "samba", "cumbia"]):
            categories["Musical Styles"].append(basename)
            categorized = True
        # Rudiments
        elif "rudiments" in tags or any(r in lower_name for r in ["paradiddle", "roll", "flam", "drag", "ruff", "stroke_roll", "diddle", "herta"]):
            categories["Rudiments"].append(basename)
            categorized = True
        # Theory/Notation
        elif "theory" in tags or "notation" in tags or any(t in lower_name for t in ["time_signature", "note", "rest", "meter", "measure", "clef", "tempo", "dynamics", "staccato"]):
            categories["Music Theory & Notation"].append(basename)
            categorized = True
        # Techniques
        elif "technique" in tags or "articulation" in tags or any(t in lower_name for t in ["stroke", "grip", "articulation", "hand", "foot", "wrist", "heel", "ankle", "fulcrum"]):
            categories["Techniques & Articulations"].append(basename)
            categorized = True
        # Instruments
        elif "drum" in tags or any(i in lower_name for i in ["bass_drum", "snare", "hi-hat", "ride", "tom", "cymbal", "beater", "kit", "seat"]):
            categories["Instruments & Gear"].append(basename)
            categorized = True
        # Studies
        elif "performance" in tags or "song" in tags or "unit" in lower_name or "study" in lower_name or "IMG_" in lower_content:
            categories["Song Studies & Performances"].append(basename)
            categorized = True
        
        if not categorized:
            categories["General Concepts"].append(basename)

    # Build the Topics.md content
    index_content = "---\ntype: index\ntitle: 全域主題索引 (Global Topics Index)\nlast_updated: 2026-04-20\n---\n\n"
    index_content += "# 全域主題索引 (Global Topics Index)\n\n"
    index_content += "本頁面是 Groove Hub 知識網絡的全自動化索引。所有節點均依據語義標籤進行分類，確保知識的高可觸達性。\n\n"
    
    for cat, items in categories.items():
        if not items: continue
        index_content += f"## {cat}\n"
        # Sort items for readability
        sorted_items = sorted(list(set(items)))
        for item in sorted_items:
            index_content += f"- [[{item}|{item.replace('_', ' ')}]]\n"
        index_content += "\n"

    index_path = os.path.join(topics_dir, 'Topics_Index.md')
    with open(index_path, 'w', encoding='utf-8') as file:
        file.write(index_content)
    
    print(f"Generated Topics Index with {sum(len(v) for v in categories.values())} entries.")

if __name__ == "__main__":
    generate_topics_index('c:/Users/USER/.gemini/antigravity/scratch/drum-llm-wiki/wiki')
