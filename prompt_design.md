# Prompt Design Document

## Overview

This document explains the prompt engineering strategy used in the OLAP BI Assistant.

---

## System Prompt Architecture

The system prompt is the cornerstone of this application. It functions as a **declarative program** written in English, defining:

1. **Data Contract** – exact column names, types, and value ranges the LLM can reference
2. **Operation Taxonomy** – precise definitions of each OLAP operation with examples
3. **Output Schema** – a strict JSON structure the LLM must always return
4. **Pandas Rules** – constraints on how the LLM writes executable code

### Why a Single System Prompt?

A single, comprehensive system prompt was chosen over few-shot chaining because:
- The dataset schema is static and well-defined
- OLAP operations map cleanly to pandas idioms
- A JSON contract makes parsing deterministic and error-proof

---

## Output Schema Design

Every LLM response follows this JSON schema:

```json
{
  "operation":    "slice|dice|group_summarize|drill_down|roll_up|compare|overview",
  "description":  "Human-readable explanation of the analysis",
  "pandas_code":  "Executable pandas code that creates df_result",
  "chart_type":   "bar|line|pie|table|none",
  "chart_config": { "x": "col", "y": "col", "color": "col|null", "title": "str" },
  "insight":      "1-2 sentence business narrative",
  "follow_ups":   ["question1", "question2", "question3"]
}
```

**Rationale for each field:**

| Field | Why It Exists |
|-------|---------------|
| `operation` | Enables badge display; allows filtering by OLAP type |
| `description` | Provides transparency — user sees what analysis was run |
| `pandas_code` | Separates AI reasoning from computation (LLM thinks, Python computes) |
| `chart_type` | LLM selects the most appropriate visualization for the data |
| `chart_config` | Decouples chart logic from rendering code |
| `insight` | Adds interpretive layer — transforms numbers into business language |
| `follow_ups` | Drives conversational exploration; mirrors how analysts actually work |

---

## OLAP Operation Mapping

| User Intent | OLAP Operation | Pandas Pattern |
|-------------|---------------|----------------|
| "Show only 2024" | Slice | `df[df['year']==2024]` |
| "Electronics in Europe" | Dice | `df[(df['cat']=='E') & (df['reg']=='Europe')]` |
| "Revenue by region" | Group & Summarize | `df.groupby('region').agg(...)` |
| "Break down by quarter" | Drill-Down | Filter + `groupby('quarter')` |
| "Compare 2023 vs 2024" | Compare | `groupby(['year', 'region'])` + pivot |

---

## Multi-Turn Context Strategy

The app maintains a `chat_history` list that grows with each turn. This allows:

- **Contextual drill-downs**: "Now break that down by month" refers to the previous query's filters
- **Follow-up refinement**: "Show only Corporate segment" adds to existing filters

**Limitation**: Token growth over long sessions. In production, implement a sliding window (last N turns) or summarization step.

---

## Error Handling Strategy

Three failure modes are handled gracefully:

1. **JSON parse failure** → Return `ERROR_RESPONSE` fallback, show sample data
2. **pandas exec failure** → Show warning, fall back to `df.head(10)`
3. **API error** → Surface the error message, return fallback

This ensures the app never crashes from LLM output; it degrades gracefully.

---

## Prompt Engineering Lessons

1. **Be explicit about variable names**: Specifying `df_result` prevents ambiguity in exec()
2. **Include anti-hallucination rules**: Listing exact column names prevents the LLM from inventing columns
3. **Show examples, not just instructions**: The two worked examples in the prompt dramatically improve output quality
4. **Enforce a strict output contract**: Asking for JSON inside a code block makes parsing reliable
5. **Round numeric results**: Without this instruction, LLMs sometimes produce 12+ decimal places

---

## Improvements for Production

- Add a **query classifier** pre-step to detect ambiguous queries before sending to the main prompt
- Implement **prompt caching** (Anthropic's feature) for the static system prompt to reduce latency and cost
- Add **semantic validation** of generated pandas code before execution
- Use **structured outputs / tool use** instead of JSON-in-text for more reliable parsing
