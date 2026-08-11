# PromptShrink 🗜️

> Pré-processador de prompts de IA & Suite de Engenharia de LLM — reduza tokens, economize dinheiro.

PromptShrink é uma ferramenta de linha de comando (CLI) + API backend que otimiza prompts antes de enviá-los a modelos de IA (GPT, Claude, Gemini). Além de sanitização determinística e compressão semântica, ele aplica técnicas de **Engenharia de LLM** para maximizar o retorno financeiro (ROI).

---

## 🚀 Funcionalidades & Vetores de Otimização

| Nível / Vetor | O que faz | Impacto de Economia |
|---------------|-----------|--------------------|
| **1 — Sanitização Determinística** | Remove espaços duplicados, encoding ruim, markdown desnecessário, linhas repetidas | ~5–15% |
| **2 — Tokenização e Custo** | Conta tokens reais por modelo (tiktoken / fallbacks) e calcula custos em USD | Transparência em tempo real |
| **3 — Compressão Semântica** | Heurísticas linguísticas para remover cortesias e frases verbosas (PT-BR + EN) | ~15–35% |
| **⚡ Code Stripper** | Remove docstrings, comentários (`#`, `//`, `/* */`) e linhas vazias em blocos de código | ~30–60% no código |
| **📦 Format Minifier** | Minifica JSON e XML embutidos no prompt | ~20–40% no payload |
| **💡 Output Budget Advisor** | Sugere restrições de resposta (ex: "sem introdução", "JSON puro") para economizar nos tokens de saída (que custam 3-5x mais) | **ROI de 10x a 50x** |
| **🎯 Model Router** | Classifica a complexidade da instrução e recomenda modelos equivalentes mais baratos (ex: GPT-4o → GPT-4o-mini) | **Até 94% de economia** |
| **🔄 Prompt Cache Advisor** | Reordena o prompt isolando o contexto fixo no início para aproveitar Prefix Caching das APIs (Anthropic, OpenAI, Gemini) | **Até 90% nos tokens em cache** |
| **🌐 Language Density Router** | Avalia a densidade de tokens (BPE) da instrução e sugere tradução instrucional para Inglês mantendo idioma de resposta | **~20–40% na instrução** |

---

## 🛠️ Instalação

### Requisitos
- Python 3.11+
- `pip` ou `uv`

### Com pip
```bash
pip install -e ".[dev]"
```

### Com uv
```bash
uv sync
uv run promptshrink --help
```

---

## 💻 Uso — CLI

```bash
# Pipe de texto
echo "Olá! Eu gostaria que você pudesse, por favor, me ajudar com..." | promptshrink optimize --model gpt-4o

# Otimização completa com análises avançadas de LLM Engineering
promptshrink optimize --from-file meu_prompt.txt --model gpt-4o --level moderate

# Output JSON (para integração em scripts)
promptshrink optimize --model gpt-4o --json < prompt.txt

# Ver modelos e tabela de preços
promptshrink models
```

---

## 📡 Uso — API Backend

```bash
# Iniciar o servidor
uvicorn api.main:app --reload --port 8000
# ou
make api
```

### Endpoint `POST /optimize`

```json
{
  "text": "Olá! Eu gostaria que você pudesse, por favor, me ajudar a escrever um código Python para ordenar uma lista.",
  "model": "gpt-4o",
  "level": "moderate",
  "semantic": true,
  "enable_llm_insights": true
}
```

#### Resposta JSON:

```json
{
  "original": { "text": "...", "tokens": 342, "cost_usd": 0.000855 },
  "optimized": { "text": "...", "tokens": 198, "cost_usd": 0.000495 },
  "savings": { "tokens": 144, "percent": 42.1, "cost_usd": 0.00036 },
  "diff": "...",
  "warnings": [],
  "rules_applied": ["collapse_spaces", "strip_code_comments", "please_simplify_pt"],
  "model_recommendation": {
    "current_model": "gpt-4o",
    "suggested_model": "gpt-4o-mini",
    "complexity_level": "low",
    "reasoning": "Tarefa de baixa complexidade. 'gpt-4o-mini' executa com a mesma qualidade.",
    "potential_cost_savings_usd": 0.000465,
    "percent_cheaper": 94.0
  },
  "output_budget_advice": {
    "intent_detected": "Desenvolvimento de Código",
    "suggested_constraint": "Responda APENAS com o código, sem explicações nem introdução/conclusão.",
    "prompt_tokens_added": 12,
    "est_output_tokens_saved": 150,
    "net_cost_savings_usd": 0.00147,
    "roi_multiplier": 50.0
  },
  "cache_advice": {
    "is_cacheable": true,
    "prefix_tokens": 120,
    "estimated_cache_savings_usd": 0.000225,
    "explanation": "Estruturado em prefixo cacheável..."
  },
  "language_advice": {
    "detected_language": "pt-br",
    "tokens_saved": 14,
    "percent_saved": 28.5,
    "english_instruction_prompt": "Write a Python function to sort a list.\nNote: Reply in Portuguese."
  }
}
```

---

## 🧪 Testes

```bash
make test
```

---

## 📄 Licença

MIT
