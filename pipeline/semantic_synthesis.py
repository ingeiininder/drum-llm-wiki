import os
import re
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data" / "output"
SCRATCH_DIR = ROOT_DIR / "scratch"
SCRATCH_DIR.mkdir(exist_ok=True)

KEYWORDS = ["pop", "rock", "blues", "funk", "jazz", "shuffle", "country"]

def semantic_synthesis():
    print(f"[*] Starting semantic synthesis across {len(list(DATA_DIR.glob('*.txt')))} files...")
    
    results = {k: [] for k in KEYWORDS}
    
    for fpath in DATA_DIR.glob("*.txt"):
        if fpath.name == "all_extracted_text_optimized.txt": continue
        
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        # Split by paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        for para in paragraphs:
            para_clean = para.replace('\n', ' ').strip()
            if not para_clean: continue
            
            for kw in KEYWORDS:
                if kw in para_clean.lower():
                    results[kw].append({
                        "source": fpath.name,
                        "text": para_clean
                    })

    # Save results to scratch
    output_path = SCRATCH_DIR / "semantic_matches.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"[V] Semantic synthesis complete. Results saved to {output_path}")

if __name__ == "__main__":
    semantic_synthesis()
