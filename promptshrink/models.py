"""
Modelos de dados compartilhados entre os módulos do PromptShrink.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class ModelTarget(str, Enum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"
    CLAUDE_35_SONNET = "claude-3-5-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    CLAUDE_3_OPUS = "claude-3-opus"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"
    GEMINI_20_FLASH = "gemini-2.0-flash"

    @classmethod
    def choices(cls) -> list[str]:
        return [m.value for m in cls]


class CompressionLevel(str, Enum):
    NONE = "none"        # Só sanitização
    LIGHT = "light"      # Remove cortesias óbvias
    MODERATE = "moderate"  # + frases verbosas
    AGGRESSIVE = "aggressive"  # + reescritas mais profundas


@dataclass
class TokenCount:
    model: str
    count: int
    encoding_used: str
    is_approximate: bool = False
    confidence: str = "exact"  # "exact", "estimated", "rough"


@dataclass
class CostEstimate:
    model: str
    tokens: int
    cost_usd: float
    price_per_million: float


@dataclass
class SanitizeResult:
    original: str
    sanitized: str
    rules_applied: list[str] = field(default_factory=list)

    @property
    def chars_removed(self) -> int:
        return len(self.original) - len(self.sanitized)


@dataclass
class CompressResult:
    original: str
    compressed: str
    level: CompressionLevel
    rules_applied: list[str] = field(default_factory=list)

    @property
    def chars_removed(self) -> int:
        return len(self.original) - len(self.compressed)


@dataclass
class ModelRoutingRecommendation:
    suggested_model: str
    current_model: str
    complexity_level: str  # "trivial", "low", "medium", "high"
    reasoning: str
    potential_cost_savings_usd: float
    percent_cheaper: float
    batch_api_eligible: bool = False
    batch_api_savings_usd: float = 0.0


@dataclass
class CacheAdvice:
    is_cacheable: bool
    reordered_prompt: str
    prefix_tokens: int
    estimated_cache_savings_usd: float
    explanation: str
    break_even_requests: Optional[int] = None


@dataclass
class OutputBudgetAdvice:
    intent_detected: str
    suggested_constraint: str
    prompt_tokens_added: int
    est_output_tokens_saved: int
    net_cost_savings_usd: float
    roi_multiplier: float


@dataclass
class LanguageAdvice:
    detected_language: str
    english_instruction_prompt: Optional[str]
    original_tokens: int
    translated_tokens: int
    tokens_saved: int
    percent_saved: float


@dataclass
class OptimizationMetrics:
    tokens_before: int
    tokens_after: int
    cost_before_usd: float
    cost_after_usd: float
    model: str
    semantic_similarity_score: float = 1.0
    confidence: str = "exact"

    @property
    def tokens_saved(self) -> int:
        return self.tokens_before - self.tokens_after

    @property
    def percent_saved(self) -> float:
        if self.tokens_before == 0:
            return 0.0
        return round((self.tokens_saved / self.tokens_before) * 100, 2)

    @property
    def cost_saved_usd(self) -> float:
        return round(self.cost_before_usd - self.cost_after_usd, 8)


@dataclass
class OptimizationResult:
    original_text: str
    optimized_text: str
    metrics: OptimizationMetrics
    diff_lines: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rules_applied: list[str] = field(default_factory=list)
    model_recommendation: Optional[ModelRoutingRecommendation] = None
    cache_advice: Optional[CacheAdvice] = None
    output_budget_advice: Optional[OutputBudgetAdvice] = None
    language_advice: Optional[LanguageAdvice] = None

    def to_dict(self) -> dict:
        m = self.metrics
        res: dict[str, Any] = {
            "original": {
                "text": self.original_text,
                "tokens": m.tokens_before,
                "cost_usd": m.cost_before_usd,
                "confidence": m.confidence,
            },
            "optimized": {
                "text": self.optimized_text,
                "tokens": m.tokens_after,
                "cost_usd": m.cost_after_usd,
                "confidence": m.confidence,
            },
            "savings": {
                "tokens": m.tokens_saved,
                "percent": m.percent_saved,
                "cost_usd": m.cost_saved_usd,
            },
            "quality": {
                "semantic_similarity_score": m.semantic_similarity_score,
            },
            "diff": "\n".join(self.diff_lines),
            "warnings": self.warnings,
            "rules_applied": self.rules_applied,
        }

        if self.model_recommendation:
            mr = self.model_recommendation
            res["model_recommendation"] = {
                "current_model": mr.current_model,
                "suggested_model": mr.suggested_model,
                "complexity_level": mr.complexity_level,
                "reasoning": mr.reasoning,
                "potential_cost_savings_usd": mr.potential_cost_savings_usd,
                "percent_cheaper": mr.percent_cheaper,
                "batch_api_eligible": mr.batch_api_eligible,
                "batch_api_savings_usd": mr.batch_api_savings_usd,
            }

        if self.cache_advice:
            ca = self.cache_advice
            res["cache_advice"] = {
                "is_cacheable": ca.is_cacheable,
                "prefix_tokens": ca.prefix_tokens,
                "estimated_cache_savings_usd": ca.estimated_cache_savings_usd,
                "break_even_requests": ca.break_even_requests,
                "explanation": ca.explanation,
                "reordered_prompt": ca.reordered_prompt,
            }

        if self.output_budget_advice:
            ob = self.output_budget_advice
            res["output_budget_advice"] = {
                "intent_detected": ob.intent_detected,
                "suggested_constraint": ob.suggested_constraint,
                "prompt_tokens_added": ob.prompt_tokens_added,
                "est_output_tokens_saved": ob.est_output_tokens_saved,
                "net_cost_savings_usd": ob.net_cost_savings_usd,
                "roi_multiplier": ob.roi_multiplier,
            }

        if self.language_advice:
            la = self.language_advice
            res["language_advice"] = {
                "detected_language": la.detected_language,
                "original_tokens": la.original_tokens,
                "translated_tokens": la.translated_tokens,
                "tokens_saved": la.tokens_saved,
                "percent_saved": la.percent_saved,
                "english_instruction_prompt": la.english_instruction_prompt,
            }

        return res
