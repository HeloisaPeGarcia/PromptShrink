# PromptShrink 🗜️

> **AI Prompt Pre-processor & LLM Engineering Engine**
> Reduce input tokens by up to 60%, constrain costly output tokens, and save money in production.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Read this document in [Português (PT-BR)](README.md).*

---

## 🧩 New Features

### 1. 📂 Codebase Context Shrinker (`promptshrink repo`)
Scans entire code repositories, minifies code and strips comments from every file, packaging the project into a single Markdown context payload ready to paste into LLMs (Claude, GPT-4o, Gemini):
```bash
promptshrink repo --path ./src --save-to-file context.txt
```

### 2. 🧮 ROI Calculator & Cost Simulator (`promptshrink calc`)
Simulates monthly dollar savings comparing current spend vs. PromptShrink + Model Router:
```bash
promptshrink calc --calls 100000 --tokens 800 --model gpt-4o
```

### 3. 📊 Embedded Web Dashboard (`GET /dashboard`)
Real-time web analytics UI served directly by FastAPI at `http://localhost:8000/dashboard`:
- Tokens saved metrics.
- Estimated USD ($) savings.
- Percentage reduction rates and active rule breakdowns.

### 4. 🐍 Transparent Python SDK (`PromptShrinkClient`)
Clean Python wrapper for direct optimization in codebases:
```python
from promptshrink.sdk import PromptShrinkClient

client = PromptShrinkClient(default_model="gpt-4o")
optimized_text = client.optimize_text("Hello! Could you please help me with...")
```

### 5. 🧩 Web Browser Extension (`/extension`)
Manifest V3 Web Extension adding a **`🗜️ Shrink`** button to **ChatGPT**, **Claude.ai**, **Google AI Studio**, and **Poe.com**:
- Install: `chrome://extensions/` ➔ *Load unpacked* ➔ select `extension/` directory.

---

## 🎯 Overview

PromptShrink is a comprehensive **CLI + Backend API (FastAPI) + Python SDK + Web Extension** designed for developers and LLM Engineers consuming OpenAI, Anthropic, or Google Gemini APIs.

---

## 🛠️ Installation & Setup

```bash
git clone https://github.com/user/promptshrink.git
cd promptshrink
pip install -e ".[dev]"
```

---

## 💻 CLI Usage

```bash
# 1. Optimize prompt via stdin
echo "Hello! I would like you to please help me with..." | promptshrink optimize --model gpt-4o

# 2. Package and shrink an entire codebase
promptshrink repo --path ./src --save-to-file context.txt

# 3. Simulate monthly savings
promptshrink calc --calls 100000 --tokens 800 --model gpt-4o

# 4. List supported models and prices
promptshrink models
```

---

## 📡 API Reference (FastAPI)

```bash
uvicorn api.main:app --reload --port 8000
```
- OpenAPI Swagger: `http://localhost:8000/docs`
- Web Dashboard: `http://localhost:8000/dashboard`

---

## 📄 License

Distributed under the **MIT** License. See `LICENSE` for details.
