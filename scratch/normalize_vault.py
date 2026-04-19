import os
import re

def normalize_vault(wiki_dir):
    topics_dir = os.path.join(wiki_dir, 'topics')
    all_files = [f for f in os.listdir(topics_dir) if f.endswith('.md')]
    
    # 1. Rename files with spaces
    rename_count = 0
    for f in all_files:
        if ' ' in f:
            new_f = f.replace(' ', '_')
            os.rename(os.path.join(topics_dir, f), os.path.join(topics_dir, new_f))
            rename_count += 1
    
    print(f"Renamed {rename_count} files (spaces to underscores).")
    
    # 2. Update all internal links inside file content to use underscores
    # Re-list after renames
    all_files_new = [f for f in os.listdir(topics_dir) if f.endswith('.md')]
    
    update_count = 0
    for f in all_files_new:
        path = os.path.join(topics_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Link pattern [[Target|Alias]] or [[Target]]
        def fix_link(match):
            inner = match.group(1)
            parts = inner.split('|')
            target = parts[0].strip().replace(' ', '_')
            if len(parts) > 1:
                return f"[[{target}|{parts[1]}]]"
            return f"[[{target}]]"
            
        new_content = re.sub(r'\[\[(.*?)\]\]', fix_link, content)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            update_count += 1
            
    print(f"Updated internal links in {update_count} files.")

if __name__ == "__main__":
    normalize_vault('c:/Users/USER/.gemini/antigravity/scratch/drum-llm-wiki/wiki')
