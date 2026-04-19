import os
import re

def semantic_linker(wiki_dir):
    topics_dir = os.path.join(wiki_dir, 'topics')
    all_files = [f for f in os.listdir(topics_dir) if f.endswith('.md')]
    
    # 1. Build dictionary of all possible node names (stripped of extension)
    # Sort by length descending to match longest phrases first (e.g., "Bass Drum Technique" before "Bass Drum")
    node_names = sorted([f[:-3] for f in all_files if f != 'Dashboard.md'], key=len, reverse=True)
    
    # Create word-to-filename mapping (though they are basically the same here)
    name_to_file = {name: name for name in node_names}
    
    # Pre-compile regex for each name to avoid massive compute inside loops
    # Use word boundaries \b to avoid matching "Paradid" in "Paradiddle"
    # Replace underscores with spaces for matching text content
    compiled_patterns = []
    for name in node_names:
        readable_name = name.replace('_', ' ')
        # Escape for regex and ensure case insensitive matching
        pattern = re.compile(r'\b(' + re.escape(readable_name) + r')\b', re.IGNORECASE)
        compiled_patterns.append((pattern, name))

    changed_count = 0
    total_links_added = 0

    for f in all_files:
        path = os.path.join(topics_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        orig_content = content
        
        # 2. Extract already linked targets to avoid double linking
        existing_links = set(re.findall(r'\[\[(.*?)\]\]', content))
        existing_targets = {L.split('|')[0].strip().replace(' ', '_') for L in existing_links}
        
        # Current file's own name should not be linked to itself
        current_name = f[:-3]
        
        new_content = content
        
        # Split content into parts: inside [[links]], inside code blocks, and the rest (text)
        # We only want to replace in "rest (text)"
        # Simple approach for a hacky script: iterate patterns
        for pattern, target in compiled_patterns:
            if target == current_name or target in existing_targets:
                continue
            
            # Complex replacement to avoid breaking existing markdown syntax
            # We skip if the word is already inside [[]] or []() or `code`
            def replace_if_free(match):
                word = match.group(0)
                pos = match.start()
                
                # Check if inside [[ ]]
                prefix = new_content[:pos]
                if prefix.count('[[') > prefix.count(']]'):
                    return word # Already in a link
                
                # Check if inside code block
                if prefix.count('`') % 2 != 0:
                    return word # In code
                
                nonlocal total_links_added
                total_links_added += 1
                return f"[[{target}|{word}]]"

            new_content = pattern.sub(replace_if_free, new_content)

        if new_content != orig_content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            changed_count += 1

    print(f"--- Semantic Linker Report ---")
    print(f"Files Processed: {len(all_files)}")
    print(f"Files Modified: {changed_count}")
    print(f"New Links Created: {total_links_added}")
    print(f"------------------------------")

if __name__ == "__main__":
    semantic_linker('c:/Users/USER/.gemini/antigravity/scratch/drum-llm-wiki/wiki')
