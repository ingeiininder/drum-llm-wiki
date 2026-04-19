# Drum-LLM-Wiki Schema & Conventions

This document defines the architecture, data standards, and maintenance rules for the **Drum-LLM-Wiki**. All AI agents maintaining this vault must adhere to these conventions to ensure consistent, high-density knowledge synthesis.

## 1. Node Types (節點類型)

Every document in the wiki must have a `type` defined in its YAML frontmatter:

- **Style Hub**: Root nodes for musical genres (e.g., `Pop-Rock_Drumming`). Focuses on "Aesthetic -> Sound -> Technique" mapping.
- **Technique**: Physical execution details (e.g., `Bass_Drum_Technique`). Focuses on "Mechanics -> Variations -> Stylistic Context".
- **Concept**: Theoretical principles (e.g., `Syncopation`, `Subdividing`).
- **Entity**: People, brands, or bands (e.g., `Steve_Jordan`, `Yamaha_Drums`).
- **Index**: Navigation nodes (e.g., `Dashboard`, `Topics_Index`).

## 2. Language & Terminology (語言與用語規範)

- **Language**: Strict **Traditional Chinese (Taiwan Usage)**.
- **Prohibited Terms (禁用詞)**: 視頻 (❌) -> 影片 (✅), 質量 (❌) -> 品質 (✅), 項目 (❌) -> 專案 (✅), 鏈接 (❌) -> 連結 (✅).
- **English Keywords**: Professional terminology should keep English counterparts in parentheses where helpful (e.g., 埋槌 (Burying the beater)).

## 3. Metadata Standards (元數據規範)

Every node must contain:
```yaml
---
type: [type_name]
source: [List of Source IDs, e.g., IMG_xxxx]
tags: [Relevant tags]
last_updated: [YYYY-MM-DD]
---
```

## 4. Maintenance SOP (維護標準流程)

### Ingest (錄入)
When adding new content from `data/output/`:
1.  **Synthesize**: Do not just copy/paste. Integrate new info into existing Topic or Style pages.
2.  **Cross-Link**: Every technical term mentioned must be linked using `[[Word]]`.
3.  **Summarize**: Update `Topics_Index.md` with a one-line summary of the new/updated node.

### Lint (校閱)
Regularly check for:
1.  **Orphans**: Ensure no page is disconnected from the network.
2.  **Naming**: Filenames must use underscores (`_`) instead of spaces.
3.  **Ambiguity**: If two textbook sources contradict each other, flag it in a "Pedagogical Note" section.

### Version Control (版本控制)
**Mandatory after every major task batch**:
1.  **Commit**: Use descriptive commit messages (e.g., `feat: enrich index summaries`).
2.  **Push**: Must perform `git push` immediately after commit to ensure multi-device synchronization.

## 5. Visual Standards (視覺規範)
- Use **Mermaid diagrams** for complex relationships.
- Use **Markdown tables** for technical comparisons.
- References to charts must use the `[IMG_xxxx]` ID format to allow future automated image binding.

---
*Inspired by Andrej Karpathy's llm-wiki pattern.*
