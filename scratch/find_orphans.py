import os
import re

def find_orphans(wiki_dir):
    topics_dir = os.path.join(wiki_dir, 'topics')
    if not os.path.isdir(topics_dir):
        print(f"Error: {topics_dir} not found.")
        return

    all_files = [f for f in os.listdir(topics_dir) if f.endswith('.md')]
    all_basenames = {f[:-3] for f in all_files}
    
    # Map of filename -> set of outgoing links
    outgoing_links = {}
    # Track which files are linked TO
    linked_to = set()

    for f in all_files:
        path = os.path.join(topics_dir, f)
        basename = f[:-3]
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Find [[Link]] or [[Link|Alias]]
            links = re.findall(r'\[\[(.*?)\]\]', content)
            
            clean_links = set()
            for L in links:
                target = L.split('|')[0].strip().replace(' ', '_')
                clean_links.add(target)
                linked_to.add(target)
            
            outgoing_links[basename] = clean_links

    # Orphan = in all_files but NOT in linked_to
    orphans = [f for f in all_files if f[:-3] not in linked_to and f != 'Dashboard.md']
    
    print(f"--- Wiki Health Report ---")
    print(f"Total Topic Nodes: {len(all_files)}")
    print(f"Orphan Nodes Found: {len(orphans)}")
    print(f"--------------------------")
    
    if orphans:
        print("\nTop 50 Orphans:")
        for o in sorted(orphans)[:50]:
            print(f"- {o}")
    
    return orphans

if __name__ == "__main__":
    find_orphans('c:/Users/USER/.gemini/antigravity/scratch/drum-llm-wiki/wiki')
