# Groove Hub Knowledge Brain: Wiki Schema

This document defines the architecture, operational protocols, and maintenance guidelines for the Groove Hub LLM Wiki.
All AI agents and collaborators operating in this project must adhere to these protocols to ensure session continuity and knowledge consistency.

---

## Negative Constraints (STRICT — Non-negotiable)
- **NO EMOJIS**: Strictly forbidden in all markdown nodes and metadata.
- **NO DECORATIVE ICONS**: Do not use non-textual symbols for visual styling.
- **NO DECORATIVE FORMATTING**: Avoid excessive use of separators or decorative elements.

---

## 1. Design Philosophy (Karpathy LLM-Wiki Pattern)

This project implements the **LLM-Wiki architecture** described by Andrej Karpathy:

> Instead of RAG (retrieve-at-query-time), the LLM incrementally builds and maintains a **persistent, compounding wiki**.
> Knowledge is compiled once and kept current — not re-derived on every query.

### Three-Layer Architecture

| Layer | Location | Owner | Rule |
|-------|----------|-------|------|
| Raw Sources | `data/output/*.txt` | Human | Immutable. LLM reads, never modifies. |
| The Wiki | `wiki/topics/`, `wiki/exercises/`, `wiki/entities/` | LLM | LLM creates and updates. Human reads. |
| The Schema | `wiki/CLAUDE.md` (this file) | Co-evolved | Human + LLM update together over time. |

### Key Operations
- **Ingest**: Drop new source → LLM reads, extracts, updates relevant nodes, appends log.
- **Query**: LLM reads `index.md` first → identifies relevant nodes → drills in → answers with citations.
- **Lint**: Periodic health check — find orphan pages, contradictions, stale claims, missing links.

---

## 2. Core Principles

- **Atomicity**: Each knowledge node (.md) must handle exactly ONE core concept.
- **Link-First**: Use `[[ConceptName]]` Obsidian-style links to establish bi-directional connectivity.
- **Traceability**: Every entry must reference its source file in frontmatter (e.g., `source: IMG_0510`).
- **Information Gain**: Supplement MI curriculum text with professional context, pro-tips, and common pitfalls. Do not just transcribe — synthesize.
- **Index-First Querying**: When answering any question, read `wiki/index.md` first to locate relevant nodes before reading individual files.

---

## 3. Project Structure

```
groove-hub/
├── pipeline/
│   ├── wiki_compiler.py     # Gemini API batch compiler (V2 Optimized)
│   ├── ocr_local_easy.py    # Local OCR pipeline (EasyOCR)
│   └── build_index.py       # Auto-generates wiki/index.md (no API key needed)
├── wiki/
│   ├── CLAUDE.md            # This schema file (AI agent context)
│   ├── index.md             # LLM query navigation index (auto-generated)
│   ├── Dashboard.md         # Human-facing master index
│   ├── Welcome.md           # Vault onboarding guide
│   ├── log.md               # Append-only ingestion and operation log
│   ├── topics/              # Theory & technique nodes (755 entries)
│   ├── exercises/           # Drill & pattern nodes (310 entries)
│   └── entities/            # Instrument & people nodes (125 entries)
└── data/
    ├── input/               # (gitignored) Raw source images
    └── output/              # OCR .txt files + .processed_sources.log (Git-tracked)
```

---

## 4. Frontier Status (as of 2026-04-19)

| Metric | Value |
|--------|-------|
| Source pages digitized | 1,444 / 1,444 (100%) |
| Topics nodes | 755 |
| Exercises nodes | 310 |
| Entities nodes | 125 |
| Total nodes | 1,190 |
| Estimated internal links | 12,000+ |
| index.md | Generated (217.5 KB) |
| GitHub repo | https://github.com/ingeiininder/drum-llm-wiki |

**Current phase**: Ingestion complete. Next phase = **Lint + Query + SEO content generation**.

---

## 5. Node Metadata Schema (YAML)

Every new node must include the following frontmatter:

```yaml
---
type: topic | entity | exercise
book_id: PERF1 | READ1 | READ2 | READ3 | TECH1_2 | TECH3_4
source: IMG_XXXX
unit: [Unit Number if identified]
tags: [relevant, drumming, tags]
last_updated: YYYY-MM-DD
---
```

### Book ID Mapping

| Book ID | IMG Range | Content |
|---------|-----------|---------|
| PERF1 | 127–150 | Performance Fundamentals |
| READ1 | 151–700 | Reading & Rhythm Book 1 |
| READ2 | 701–874 | Reading & Rhythm Book 2 |
| READ3 | 875–1000 | Reading & Rhythm Book 3 |
| TECH1_2 | 1001–1250 | Technique Builder Books 1–2 |
| TECH3_4 | 1251–1500 | Technique Builder Books 3–4 |

---

## 6. Pipeline Operation Guide

### Running the Wiki Compiler

```powershell
# Set API key (required each session)
$env:GEMINI_API_KEY = "your_key_here"

# Full run — continues from last checkpoint automatically
python pipeline/wiki_compiler.py --window 25 --model gemini-2.5-flash

# Test run — process first 5 source files only
python pipeline/wiki_compiler.py --test-run 5 --window 5
```

### Rebuilding the Index

Run after any new nodes are added:

```powershell
python pipeline/build_index.py
```

### Daily Git Sync Workflow

```powershell
# Before starting work (pull latest from GitHub)
git pull

# After adding new nodes or modifying pipeline
git add .
git commit -m "feat: add new wiki nodes / fix: [description]"
git push
```

---

## 7. Cross-Machine Setup (New Computer)

```powershell
# 1. Clone full repo (includes OCR data + pipeline state)
git clone https://github.com/ingeiininder/drum-llm-wiki.git
cd drum-llm-wiki

# 2. Install dependencies
pip install google-genai easyocr

# 3. Set API key
$env:GEMINI_API_KEY = "your_key_here"

# 4. Continue wiki expansion (auto-resumes from .processed_sources.log)
python pipeline/wiki_compiler.py --window 25 --model gemini-2.5-flash
```

> **Note**: `data/input/` (raw images) is gitignored and must be copied manually if re-OCR is needed.
> Since ingestion is 100% complete, re-OCR is currently unnecessary.

---

## 8. Safe Operations Protocol (CVD Protocol)

> **CAUTION**: Simultaneous delete/move operations on primary data are strictly prohibited.

Follow **Copy-Verify-Delete (CVD)** for any large-scale restructuring:

1. **Copy**: Use `Copy-Item` to backup data to the target path.
2. **Verify**: Check file count + directory size + readability at destination.
3. **Delete**: Only run `Remove-Item` after successful verification.

### Forbidden Operations
- Do NOT use `Move-Item` on non-backed-up primary sources.
- Do NOT chain destructive commands with `;` or `&&` without safety checks.
- Do NOT use `-Force` flags unless necessary and explicitly documented.

---

## 9. Known Gaps & Next Actions

| Gap | Priority | Action |
|-----|----------|--------|
| **Lint pass** — find orphan nodes, contradictions, stale claims | High | Run LLM lint session against wiki |
| **index.md freshness** — rebuild after any new nodes added | Medium | `python pipeline/build_index.py` |
| **SEO content generation** — use wiki as knowledge base for articles | Medium | Use `seo-content-writer` skill |
| **data/input/ backup** — original images not in Git | Low | Keep local copy on primary machine |
| **query.md pattern** — file notable Q&A back into wiki as new nodes | Low | Implement per Karpathy "Query" operation |

---

## 10. Language Protocol

| Context | Language |
|---------|----------|
| Wiki node content | **Professional English** (AI-facing, SEO-optimized) |
| Dashboard, log, CLAUDE.md UI | **Traditional Chinese** (human-facing) |
| Code comments, pipeline scripts | English |
| Emoji usage | **Strictly prohibited everywhere** |
