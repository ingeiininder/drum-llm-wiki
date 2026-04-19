import os
import re
import time
import argparse
from pathlib import Path
from google import genai
from google.genai import types

ROOT_DIR = Path(__file__).parent.parent
DATA_OUTPUT_DIR = ROOT_DIR / "data" / "output"
WIKI_DIR = ROOT_DIR / "wiki"
TOPICS_DIR = WIKI_DIR / "topics"
ENTITIES_DIR = WIKI_DIR / "entities"
EXERCISES_DIR = WIKI_DIR / "exercises"

# Progress persistence log
PROCESSED_LOG = DATA_OUTPUT_DIR / ".processed_sources.log"

for d in [TOPICS_DIR, ENTITIES_DIR, EXERCISES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

SYSTEM_INSTRUCTION = """
You are the "Groove Hub Knowledge Compiler," an expert percussion educator and technical content architect. Your mission is to transform unstructured OCR text (derived from Musicians Institute percussion curricula) into structured, interlinked Markdown wiki entries.

### 1. Style and Language (CRITICAL):
- **Language**: Use **Professional English** for all content. Maintain the technical fidelity of the original Musicians Institute curriculum.
- **Tone**: Educational, authoritative, and concise.

### 2. Core Guidelines:
- **Atomicity**: Deconstruct the text into individual, atomic concepts. Each file (.md) should cover exactly ONE topic, entity, or exercise.
- **Bi-directional Linking**: Use `[[Concept Name]]` to link to other existing or potential entries. Link technical terms, techniques, instruments, and authors.
- **Information Gain**: Enrich the entries with professional context, "pro-tips," and common pitfalls. Do not just transcribe; synthesize.
- **Traceability**: Always include the source filename (e.g., IMG_0130) in the frontmatter.

### 3. Required Frontmatter Schema (YAML):
---
type: [topic | entity | exercise]
source: [Source identifiers, e.g., IMG_0130, IMG_0131]
unit: [Original unit/module if identified]
tags: [Relevant drumming tags]
last_updated: [YYYY-MM-DD]
---

### 4. Output Format:
Wrap each extracted entry exactly as follows:

---BEGIN_NODE: Concept_Name.md---
[YAML Frontmatter]

# Concept Name
[Enriched English content with high density of internal linking]
---END_NODE---

Output ONLY the ---BEGIN_NODE to ---END_NODE blocks.
"""

def load_processed_sources():
    if PROCESSED_LOG.exists():
        with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def mark_sources_processed(sources):
    with open(PROCESSED_LOG, "a", encoding="utf-8") as f:
        for s in sources:
            f.write(f"{s}\n")

def call_api(client, model_name, prompt, sources, max_retries=6):
    for attempt in range(max_retries):
        if attempt == 0:
            print(f"[*] Dispatching to API ({len(sources)} pages)...")
        else:
            print(f"[*] Retry #{attempt+1} ({len(sources)} pages)...")
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2
                )
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            print(f"[!] API Error ({sources}): {error_msg}")
            
            # Rate limit handling for free API tier
            if "503" in error_msg or "429" in error_msg:
                if "quota" in error_msg.lower():
                    print(f"    [!] FATAL: API Quota Exceeded for today.")
                    exit(1)
                
                wait_time = 10 * (2 ** attempt)
                print(f"    -> Rate limit / Server busy. {wait_time}s cooldown...")
                time.sleep(wait_time)
            elif "404" in error_msg:
                print("    -> Model name error.")
                break
            else:
                break
            
    print(f"[!] Continuous retry failure, skipping block ({sources})")
    return None

def write_nodes(response_text, cvd_safe=True):
    if not response_text:
        return 0

    pattern = re.compile(r'---BEGIN_NODE:\s*(.+?\.md)\s*---\n?(.*?)\n?---END_NODE---', re.DOTALL)
    matches = pattern.findall(response_text)

    if not matches:
        print("[-] No new knowledge nodes extracted from this segment.")
        return 0

    saved_count = 0
    for filename, content in matches:
        # Sanitize filename: remove spaces, replace illegal characters with hyphens
        # Illegal in Windows: < > : " / \ | ? *
        filename = re.sub(r'[<>:"/\\|?*]', "-", filename.strip())
        content = content.strip()

        node_type = "topic"
        m = re.search(r'^type:\s*(topic|entity|exercise)', content, re.MULTILINE | re.IGNORECASE)
        if m:
            node_type = m.group(1).lower()

        if node_type == "topic":
            target_path = TOPICS_DIR / filename
        elif node_type == "entity":
            target_path = ENTITIES_DIR / filename
        elif node_type == "exercise":
            target_path = EXERCISES_DIR / filename
        else:
            target_path = TOPICS_DIR / filename 

        if cvd_safe and target_path.exists():
            print(f"    [-] Node already exists, skipping overwrite: {filename}")
            continue

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"    [+] {node_type}/{filename}")
        saved_count += 1
        
    return saved_count

def get_book_id(filename):
    """Determines the MI Book ID based on the IMG number sequence."""
    try:
        # Extract number from "IMG_0521"
        num_str = "".join(filter(str.isdigit, filename))
        if not num_str: return "UNKNOWN"
        num = int(num_str)
        # Mapping ranges based on manual audit
        if 127 <= num <= 150: return "PERF1"
        if 151 <= num <= 700: return "READ1"
        if 701 <= num <= 874: return "READ2"
        if 875 <= num <= 1000: return "READ3"
        if 1001 <= num <= 1250: return "TECH1_2"
        if 1251 <= num <= 1500: return "TECH3_4"
        return "MI_CURR"
    except:
        return "UNKNOWN"

def compile_wiki(client, model_name, test_run=None, window_size=10):
    processed_sources = load_processed_sources()
    
    all_files = []
    for f in sorted(DATA_OUTPUT_DIR.glob("*.txt")):
        if f.name == "all_extracted_text_optimized.txt":
            continue
        if f.stem in processed_sources:
            continue
        all_files.append(f)
    
    print(f"[*] Discovered {len(all_files)} unprocessed files.")

    if test_run:
        all_files = all_files[:test_run]

    batch_texts = []
    batch_sources = []

    for idx, fpath in enumerate(all_files):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
            if len(text.strip()) > 10: 
                batch_texts.append(text)
                batch_sources.append(fpath.stem)
        
        if len(batch_texts) >= window_size or idx == len(all_files) - 1:
            if not batch_texts: break
            
            # Determine book ID from the first file in batch
            current_book = get_book_id(batch_sources[0])

            prompt = f"""
{SYSTEM_INSTRUCTION}

### CONTEXT:
- **Book ID**: {current_book}
- **Source Files**: {", ".join(batch_sources)}

### TASK:
Extract percussion wiki entries from the following OCR texts.
For each entry (BEGIN_NODE), include ONLY this YAML schema:
---
type: [topic | entity | exercise]
book_id: {current_book}
source: [Specific IMG_XXXX]
unit: [Original Unit #]
tags: [Relevant tags]
last_updated: 2026-04-19
---

### OCR TEXTS:
"""
            for i, txt in enumerate(batch_texts):
                prompt += f"\n--- SOURCE: {batch_sources[i]} ---\n{txt}\n"

            print(f"[*] Processing batch ({len(batch_texts)} pages: {batch_sources[0]}~{batch_sources[-1]})...")
            response_text = call_api(client, model_name, prompt, batch_sources)
            
            if response_text is not None:
                write_nodes(response_text)
                mark_sources_processed(batch_sources)
            
            print(f"[*] Cooling down for 5s to protect API quota...")
            time.sleep(5)
            
            batch_texts = []
            batch_sources = []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Groove Hub Wiki Compiler - Free Tier Optimized")
    parser.add_argument("--test-run", type=int, default=None, help="Test run with first N files only")
    parser.add_argument("--window", type=int, default=10, help="Sliding window size (batching X pages to save quota)")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="Model name (e.g., gemini-1.5-flash as backup)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] FATAL: GEMINI_API_KEY not found in environment")
        exit(1)

    print("=== Initializing Groove Hub Wiki Compiler (V2: Optimized) ===")
    print(f"* Engine: {args.model}")
    print(f"* Batch Size: Merging {args.window} pages to minimize API calls")
    print(f"* Safety: 15 RPM Throttling enabled (5s cooldown) with auto-save")
    print("=============================================================")

    client = genai.Client()
    compile_wiki(client, args.model, test_run=args.test_run, window_size=args.window)
    print("\n[V] Mission accomplished or paused by user.")
