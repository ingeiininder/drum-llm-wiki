# Groove Hub

> A structured, interlinked percussion knowledge base derived from 1,444 pages of Musicians Institute (MI) curriculum.

## Overview

**Groove Hub** is an automated knowledge management system that transforms raw, image-based MI percussion textbooks into a high-fidelity, machine-readable Markdown wiki — optimized for both human learning (Obsidian) and AI retrieval (SEO / GEO content generation).

## Knowledge Base Stats

| Category | Count |
|----------|-------|
| Topics (theory & technique) | 755 |
| Exercises (drills & patterns) | 310 |
| Entities (instruments, authors, brands) | 125 |
| **Total Nodes** | **1,190** |
| Source Pages Processed | 1,444 / 1,444 (100%) |
| Internal Links (estimated) | 12,000+ |

## Repository Structure

```
groove-hub/
├── pipeline/
│   ├── wiki_compiler.py     # Gemini API batch compiler (V2 Optimized)
│   └── ocr_local_easy.py    # Local OCR pipeline (EasyOCR)
├── wiki/
│   ├── Dashboard.md         # Master index
│   ├── Welcome.md           # Vault onboarding guide
│   ├── log.md               # Ingestion & development log
│   ├── CLAUDE.md            # AI agent context file
│   ├── topics/              # 755 theory & technique nodes
│   ├── exercises/           # 310 drill & pattern nodes
│   └── entities/            # 125 instrument & people nodes
└── data/                    # (gitignored) Raw OCR data
    ├── input/               # Source images
    └── output/              # Extracted .txt files
```

## Pipeline Architecture

```
[Raw Images] → [EasyOCR / ocr_local_easy.py] → [.txt files]
                                                      ↓
                                           [wiki_compiler.py]
                                           (Gemini Flash API)
                                                      ↓
                                    [Structured .md wiki nodes]
                                    (topics / exercises / entities)
```

## Protocols

| Protocol | Standard |
|----------|----------|
| Content Language | **Professional English** (AI-facing) |
| UI / Log Language | **Traditional Chinese** (human-facing) |
| Emoji Policy | **Strictly Prohibited** |
| Linking Format | `[[WikiLink]]` Obsidian-style |
| Frontmatter | `type`, `book_id`, `source`, `unit`, `tags`, `last_updated` |

## Running the Pipeline

```bash
# Install dependencies
pip install google-genai easyocr

# Set API key
export GEMINI_API_KEY="your_key_here"

# Run wiki compiler (full batch, window size 25)
python pipeline/wiki_compiler.py --window 25 --model gemini-2.5-flash

# Test run (first 5 files only)
python pipeline/wiki_compiler.py --test-run 5 --window 5
```

## Source Material

Based on the **Musicians Institute (MI)** percussion curriculum series:

| Book ID | Content Range |
|---------|---------------|
| PERF1 | Performance Fundamentals |
| READ1–3 | Reading & Rhythm (Books 1–3) |
| TECH1_2 | Technique Builder (Books 1–2) |
| TECH3_4 | Technique Builder (Books 3–4) |

## License

This repository contains only the pipeline scripts and structured knowledge output. All source curriculum content is © Musicians Institute. This project is for personal educational use.
