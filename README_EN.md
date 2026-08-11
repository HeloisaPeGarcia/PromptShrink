# PromptShrink 🗜️

> **AI Prompt Pre-processor & LLM Engineering Engine**
> Reduce input tokens by up to 60%, constrain costly output tokens, and save money in production.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Read this document in [Português (PT-BR)](README.md).*

---

## 🧩 Latest Feature: Web Browser Extension (`/extension`)

**PromptShrink** now features a Web Extension (Manifest V3) that injects a **`🗜️ Shrink`** button directly into the text input boxes of **ChatGPT**, **Claude.ai**, **Google AI Studio**, and **Poe.com**.

### 🌟 Extension Highlights:
- **1-Click Optimization:** Minify and shrink prompts right inside the browser interface without switching tabs.
- **Real-Time Token Savings Toast:** Displays instant token reduction feedback (e.g. `-144 tokens (-42.1%)`).
- **Resilient Hybrid Engine:** Connects to the local API (`http://localhost:8000/v1/optimize`) or uses a fast client-side JavaScript fallback engine if the local API server is offline.
- **Context Menu Integration:** Right-click any selected text on any webpage to shrink and optimize it.

### 📥 How to Install the Extension:
1. Open `chrome://extensions/` in your browser (Chrome, Edge, Brave).
2. Enable **Developer Mode** in the top-right corner.
3. Click **Load unpacked** and select the `extension/` directory from this repository.

---

## 🎯 Overview

PromptShrink is a comprehensive **CLI + Backend API (FastAPI) + Web Extension** designed for developers and LLM Engineers consuming OpenAI, Anthropic, or Google Gemini APIs.

Unlike naïve minifiers that break code or corrupt semantic context, PromptShrink operates with **deterministic Code Fence Protection**, **safe syntax minification**, **heuristic semantic compression**, and an advanced **LLM Engineering engine** to optimize model routing, prefix caching, PII masking, and prompt injection protection.

---

## 📐 Architecture Pipeline

```mermaid
flowchart TD
    A[User Prompt / ChatGPT Web / Input Chat] --> B[Code Fence Protection]
    
    subgraph Deterministic Pipeline
        B --> C[1. Sanitization & NFC Normalization]
        C --> D[2. Format Minifier JSON/XML]
        D --> E[3. Code Stripper Python tokenize / Generic]
        E --> F[4. Verbose Connectives Normalizer]
        F --> G[5. Heuristic Semantic Compression PT/EN]
    end
    
    G --> H[Code Fence Restore]
    H --> I[Tokenization & Cost Estimation]
    
    subgraph LLM Engineering Engines
        I --> J1[Output Budget Advisor ROI]
        I --> J2[Model Router & Batch API 50% Off]
        I --> J3[Prompt Cache Advisor & Break-even]
        I --> J4[Language Density Router BPE]
        I --> J5[PII Masker & Unmasker]
        I --> J6[Injection Threat Detector]
        I --> J7[Semantic Similarity Score]
    end

    J1 & J2 & J3 & J4 & J5 & J6 & J7 --> K[OptimizationResult / API JSON / CLI Rich / Extension Toast]
```

---

## 🚀 Key Features & Optimization Vectors

| Vector | Description | Savings / Impact |
|--------|-------------|------------------|
| **🧩 Web Browser Extension** | Injects `🗜️ Shrink` button into ChatGPT, Claude, Gemini, Poe | **Browser Productivity & Savings** |
| **1 — Deterministic Sanitization** | Strips invisible spaces, curly quotes, empty markdown, duplicated lines | **~5–15%** |
| **2 — Code Stripper (`tokenize`)** | Removes docstrings, comments (`#`, `//`, `/* */`), and blank lines in code blocks without breaking f-strings | **~30–60% in code** |
| **3 — Format Minifier** | Minifies embedded JSON and XML payloads in prose or blocks | **~20–40% in payload** |
| **4 — Semantic Compression** | Language heuristics removing polite fluff and filler phrases (PT-BR + EN) | **~15–35%** |
| **💡 Output Budget Advisor** | Suggests instruction constraints to cap output tokens (which cost 3-5x more) | **10x to 50x ROI** |
| **🎯 Model Router Advisor** | Assesses prompt complexity, recommends safe downgrades (e.g. GPT-4o → GPT-4o-mini), and signals Batch API eligibility | **Up to 94% cost reduction** |
| **🔄 Prompt Cache Advisor** | Reorders stable context to trigger Prefix Caching with provider-specific Break-even math | **Up to 90% in cache reads** |
| **🌐 Language Density Router** | Evaluates BPE token density (PT vs EN) and suggests English instructions with Portuguese response | **~20–40% in instructions** |
| **💬 Chat History Compressor** | Optimizes multi-turn message arrays while preserving recent N messages intact | **~30–50% in long chats** |
| **🛡️ PII Masker & Unmasker** | Masks CPF, Email, Phone, CNPJ, and Credit Cards with neutral placeholders | **Security & Privacy** |
| **⚠️ Prompt Injection Detector** | Identifies prompt injection attempts and jailbreaks with risk scoring | **Attack Mitigation** |

---

## 📊 Provider Cache Discount & Break-even Breakdown

Different LLM providers implement distinct policies for **Prompt Caching**:

```
Anthropic Claude ──► Read: 90% OFF (0.10x)  │ Write: 1.25x (Overhead) ──► Break-even: 2 requests
OpenAI GPT ───────► Read: 50% OFF (0.50x)  │ Write: 1.00x            ──► Break-even: 2 requests
Google Gemini ────► Read: 75% OFF (0.25x)  │ Write: 1.00x            ──► Break-even: 2 requests
```

---

## 🧠 Engineering & Software Design Decisions

### 1. Native `tokenize` over Regex for Python Code
- **Problem:** Simple regex for comment stripping (`#`) corrupts f-strings (`f"URL: {x}#anchor"`), embedded comments in multiline strings, or function docstrings.
- **Solution:** `code_stripper.py` leverages Python's native `tokenize` module to traverse lexical token trees, removing only genuine comments (`tokenize.COMMENT`) and standalone docstrings while preserving 100% syntactical integrity.

### 2. Unified Code Fence Protection
- **Problem:** Text sanitization, normalization, and compression rules could accidentally alter reserved terms in code (e.g., `function simply()` becoming `function()`).
- **Solution:** `code_fence.py` extracts all ` ```lang ... ``` ` blocks before any text transformations occur, replaces them with neutral placeholders (`@@PROMPTSHRINK_CODE_BLOCK_N@@`), and restores the blocks post-optimization.

### 3. N-Gram Weighted Semantic Fidelity Score
- **Problem:** Naive set comparison returns unrealistically high scores (> 95%) even when 70% of sentences are stripped.
- **Solution:** `semantic_score.py` calculates a weighted bag-of-words + **bigram** (`word_pair`) intersection matrix based on actual token frequencies, delivering realistic retention scores.

---

## 🛠️ Installation & Setup

### Requirements
- Python 3.11 or higher
- `pip` or `uv`

### Installation (Development Mode)
```bash
git clone https://github.com/user/promptshrink.git
cd promptshrink

# Using pip
pip install -e ".[dev]"

# Using uv (recommended)
uv sync
```

---

## 💻 CLI Usage

```bash
# 1. Optimize prompt via stdin
echo "Hello! I would like you to please help me with..." | promptshrink optimize --model gpt-4o

# 2. Optimize from file and save result
promptshrink optimize --from-file prompt.txt --save-to-file optimized.txt --model claude-3-5-sonnet

# 3. Dry Run (Pre-analysis of compression potential)
promptshrink optimize --from-file prompt.txt --dry-run

# 4. Automatic English instruction translation
promptshrink optimize --from-file prompt.txt --apply-language --model gpt-4o

# 5. Raw JSON Output (for scripts and pipelines)
promptshrink optimize --from-file prompt.txt --json

# 6. List supported models and price table
promptshrink models
```

---

## 📡 API Reference (FastAPI)

### Start Server
```bash
uvicorn api.main:app --reload --port 8000
# or via Makefile
make api
```
Interactive OpenAPI Swagger docs available at `http://localhost:8000/docs`.

---

## 📄 License

Distributed under the **MIT** License. See `LICENSE` for details.
