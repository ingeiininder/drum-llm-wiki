import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
WIKI_DIR = ROOT_DIR / "wiki"
TOPICS_DIR = WIKI_DIR / "topics"
EXERCISES_DIR = WIKI_DIR / "exercises"
ENTITIES_DIR = WIKI_DIR / "entities"

ALL_DIRS = [TOPICS_DIR, EXERCISES_DIR, ENTITIES_DIR]

# Manual mapping for common broken targets to existing hubs
BACKBONE_MAP = {
    # Time Signatures
    "4-4_Time": "4-4_Time_Signature",
    "4/4_Time": "4-4_Time_Signature",
    "2/4_Time": "2-4_Time_Signature",
    "3/4_Time": "3-4_Time_Signature",
    "4-4_Time_Feel": "4-4_Time_Signature",
    "3/4_Time_Feel": "3-4_Time_Signature",
    "Time_Signatures": "Time_Signature",
    "Note_Values": "Note_Value",
    "Eighth_Notes": "Eighth_Note",
    "Quarter_Notes": "Quarter_Note",
    "Half_Notes": "Half_Note",
    "Whole_Notes": "Whole_Note",
    "Sixteenth_Notes": "16th_Notes", # existing node stem
    "16th-Note_Subdivisions": "Subdivision",
    
    # Techniques
    "Accent_Patterns": "Accents_Drumming",
    "Accents": "Accents_Drumming",
    "Drum_Beat": "Groove",
    "Drum_Beats": "Groove",
    "Internal_Pulse": "Pulse",
    "Sound": "Stylistically_Correct_Drum_Sound",
    "Structure": "Phrasing",
    "Musical_Form": "Phrasing",
    "Song_Form": "Phrasing",
    
    # Notation
    "Bar_Line": "Bar_Lines",
    "System": "Chart",
    "Chart_Reading": "Chart",
    "Reading": "Sight_Reading",
}

def align_backbone():
    print(f"[*] Starting Advanced Link Alignment...")
    
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
                parts = link_text.split('|', 1)
                target = parts[0].strip()
                display = parts[1] if len(parts) > 1 else None

                # Check if target is in our manual backbone map
                if target in BACKBONE_MAP:
                    new_target = BACKBONE_MAP[target]
                    fix_count += 1
                    return f"[[{new_target}" + (f"|{display}]]" if display else "]]")
                
                return match.group(0)

            new_content = re.sub(r'\[\[([^\]]+)\]\]', replace_link, content)
            
            if new_content != content:
                fpath.write_text(new_content, encoding="utf-8")

    print(f"[V] Advanced Link Alignment complete.")
    print(f"    Processed {file_count} files.")
    print(f"    Fixed {fix_count} links.")

if __name__ == "__main__":
    align_backbone()
