"""
Pipeline de otimização: orquestra sanitização, minificação de código/formatos,
compressão semântica, análises de LLM Engineering (Model Routing, Prompt Caching, Output Budget, Language Routing).
"""

from __future__ import annotations

from promptshrink.models import (
    CompressionLevel,
    OptimizationMetrics,
    OptimizationResult,
)
from promptshrink.sanitizer import sanitize
from promptshrink.code_stripper import strip_code_blocks
from promptshrink.format_optimizer import minify_formats
from promptshrink.normalizer import normalize_connectives_and_numbers
from promptshrink.compressor import compress
from promptshrink.tokenizer import count_tokens
from promptshrink.cost_estimator import estimate_cost
from promptshrink.diff import make_diff_lines
from promptshrink.logger import get_logger
from promptshrink.semantic_score import calculate_semantic_similarity

from promptshrink.output_budget import analyze_output_budget
from promptshrink.model_router import analyze_model_routing
from promptshrink.cache_advisor import analyze_prompt_caching
from promptshrink.language_router import analyze_language_optimization

MAX_CHARS_LIMIT = 200_000  # ~50,000 tokens máximo por prompt
logger = get_logger("promptshrink.optimizer")


def optimize(
    text: str,
    model: str = "gpt-4o",
    level: CompressionLevel = CompressionLevel.LIGHT,
    semantic: bool = True,
    strip_emojis: bool = False,
    strip_code: bool = True,
    minify_json_xml: bool = True,
    enable_llm_insights: bool = True,
) -> OptimizationResult:
    """
    Executa o pipeline completo de otimização de prompt + análises de LLM Engineering.
    """
    if len(text) > MAX_CHARS_LIMIT:
        logger.error("Prompt excede o limite máximo permitido de %d caracteres.", MAX_CHARS_LIMIT)
        raise ValueError(f"Prompt excede o limite máximo permitido de {MAX_CHARS_LIMIT} caracteres.")

    warnings: list[str] = []
    all_rules: list[str] = []

    # 1. Tokenização ANTES
    tok_before = count_tokens(text, model)
    if tok_before.is_approximate:
        warnings.append(
            f"Contagem de tokens para '{model}' é aproximada "
            f"(usando {tok_before.encoding_used})."
        )

    # 2. Sanitização determinística
    san = sanitize(text, strip_emojis=strip_emojis)
    current = san.sanitized
    all_rules.extend(san.rules_applied)

    # 3. Limpeza de blocos de código
    if strip_code:
        current, code_changed = strip_code_blocks(current)
        if code_changed:
            all_rules.append("strip_code_comments")

    # 4. Minificação de formatos (JSON / XML)
    if minify_json_xml:
        current, fmt_changed = minify_formats(current)
        if fmt_changed:
            all_rules.append("minify_json_xml_formats")

    # 5. Normalização de conectivos e numéricos
    current, norm_changed = normalize_connectives_and_numbers(current)
    if norm_changed:
        all_rules.append("normalize_connectives")

    # 6. Compressão semântica (se ativada)
    if semantic and level != CompressionLevel.NONE:
        comp = compress(current, level=level)
        current = comp.compressed
        all_rules.extend(comp.rules_applied)

    # 7. Tokenização DEPOIS
    tok_after = count_tokens(current, model)

    # 8. Estimativa de custo
    cost_before_usd = 0.0
    cost_after_usd = 0.0
    try:
        cost_before_usd = estimate_cost(tok_before.count, model).cost_usd
        cost_after_usd = estimate_cost(tok_after.count, model).cost_usd
    except ValueError as exc:
        warnings.append(str(exc))
    except Exception as exc:
        warnings.append(f"Erro ao calcular custo: {exc}")

    # 9. Diff visual
    diff_lines = make_diff_lines(text, current)

    # 10. Pontuação de similaridade semântica
    semantic_similarity = calculate_semantic_similarity(text, current)

    # 11. Análises Avançadas de Engenharia de LLM
    model_rec = None
    cache_adv = None
    out_budget = None
    lang_adv = None

    if enable_llm_insights:
        model_rec = analyze_model_routing(text, model, tokens=tok_before.count)
        cache_adv = analyze_prompt_caching(current, model, tok_before=tok_before)
        out_budget = analyze_output_budget(current, model, tok_before=tok_before)
        lang_adv = analyze_language_optimization(current, model, tok_before=tok_before)

    # 12. Métricas finais
    metrics = OptimizationMetrics(
        tokens_before=tok_before.count,
        tokens_after=tok_after.count,
        cost_before_usd=cost_before_usd,
        cost_after_usd=cost_after_usd,
        model=model,
        semantic_similarity_score=semantic_similarity,
        confidence=tok_before.confidence,
    )

    logger.info(
        "Otimização concluída. Tokens: %d -> %d (%d%% economizados). Regras: %s",
        tok_before.count,
        tok_after.count,
        metrics.percent_saved,
        all_rules,
    )

    return OptimizationResult(
        original_text=text,
        optimized_text=current,
        metrics=metrics,
        diff_lines=diff_lines,
        warnings=warnings,
        rules_applied=all_rules,
        model_recommendation=model_rec,
        cache_advice=cache_adv,
        output_budget_advice=out_budget,
        language_advice=lang_adv,
    )
