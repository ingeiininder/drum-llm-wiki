# Groove Hub Knowledge Brain: Wiki Schema

This document defines the architecture and maintenance guidelines for the Groove Hub Knowledge Brain. All AI agents operating within this project must strictly adhere to these protocols.

## Negative Constraints (STRICT)
- **NO EMOJIS**: Strictly forbidden in all markdown nodes and metadata.
- **NO DECORATIVE ICONS**: Do not use non-textual symbols for visual styling.
- **NO DECORATIVE FORMATTING**: Avoid excessive use of separators or decorative elements.

## 1. Core Principles
*   **Atomicity**: Each knowledge node (.md) must handle exactly one core concept.
*   **Link-First**: Utilize the `[[TopicName]]` syntax to establish multi-directional connectivity.
*   **Traceability**: Every entry must reference its original source curriculum (e.g., `source: IMG_0510.PNG`).
*   **Information Gain**: Proactively supplement MI curriculum text with professional insights and "pro-tips."

## 2. Project Structure
*   `projects/groove-hub/wiki/`: The primary knowledge vault.
*   `projects/groove-hub/data/`: Raw input and OCR output.
*   `projects/groove-hub/pipeline/`: Automated processing and compilation scripts.

## 3. Safe Operations Protocol (CVD Protocol)

> [!CAUTION]
> **Simultaneous delete/move operations are strictly prohibited.** To prevent data loss during large-scale restructuring, follow the **Copy-Verify-Delete (CVD)** protocol.

### The CVD Protocol Steps
1.  **Copy**: Use `Copy-Item` to backup data to the target path.
2.  **Verify**:
    *   Verify file count and total directory size.
    *   Ensure data integrity and readability at the destination.
3.  **Delete**: Only perform `Remove-Item` on original files after successful verification.

### Forbidden Behaviors
*   Do NOT use `Move-Item` on non-backed-up primary sources.
*   Do NOT chain destructive commands with `;` or `&&` without explicit safety checks.
*   Do NOT use `-Force` flags unless absolutely necessary and documented.

## 4. Node Metadata Schema (YAML)
Every new entry must include the following frontmatter:
```markdown
---
type: topic | entity | exercise
book_id: [READ1 | TECH2 | etc.]
source: [IMG_XXXX.PNG]
unit: [Unit Number]
tags: [Drumming, Technique, MI_Series]
last_updated: 2026-04-19
---
```

## 5. Strategic Context (Karpathy Model)
This project implements the LLM-Wiki philosophy (inspired by Andrej Karpathy): "compiling" raw visual information into durable, high-leverage knowledge assets with compounding value over time.
