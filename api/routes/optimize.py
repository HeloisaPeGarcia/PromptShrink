"""
Endpoints principais de otimização:
- POST /v1/optimize (e alias /optimize)
- POST /v1/chat/compress
- POST /v1/pii/mask
- POST /v1/injection/check
- POST /v1/compressibility
- POST /v1/admin/reload-prices
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from promptshrink.models import CompressionLevel
from promptshrink.optimizer import optimize
from promptshrink.chat_compressor import compress_chat_history
from promptshrink.cost_estimator import load_custom_prices
from promptshrink.pii_detector import mask_pii, unmask_pii
from promptshrink.injection_detector import check_prompt_injection
from promptshrink.compressibility import analyze_compressibility

router = APIRouter(prefix="/v1", tags=["optimization"])
legacy_router = APIRouter(tags=["optimization"])


# ---------------------------------------------------------------------------
# Schemas de Request / Response
# ---------------------------------------------------------------------------


class OptimizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto do prompt a ser otimizado")
    model: str = Field(
        "gpt-4o",
        description="Modelo-alvo para tokenização e custo",
        examples=["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-flash"],
    )
    level: CompressionLevel = Field(
        CompressionLevel.LIGHT,
        description="Nível de compressão semântica: none / light / moderate / aggressive",
    )
    semantic: bool = Field(True, description="Se False, executa apenas sanitização (Nível 1)")
    strip_emojis: bool = Field(False, description="Remove emojis decorativos do prompt")
    strip_code: bool = Field(True, description="Remove comentários/docstrings de blocos de código")
    minify_json_xml: bool = Field(True, description="Minifica JSON/XML embutidos no prompt")
    mask_pii_data: bool = Field(False, description="Mascara dados pessoais como CPF, E-mail, Telefone")
    enable_llm_insights: bool = Field(
        True,
        description="Executa análises avançadas de LLM (Model Router, Caching, Output Budget, Language Density)",
    )


class TextWithMetrics(BaseModel):
    text: str
    tokens: int
    cost_usd: float
    confidence: str = "exact"


class SavingsMetrics(BaseModel):
    tokens: int
    percent: float
    cost_usd: float


class QualityMetrics(BaseModel):
    semantic_similarity_score: float = 1.0


class OptimizeResponse(BaseModel):
    original: TextWithMetrics
    optimized: TextWithMetrics
    savings: SavingsMetrics
    quality: QualityMetrics
    diff: str
    warnings: list[str]
    rules_applied: list[str]
    pii_masked_data: Optional[dict[str, str]] = None
    model_recommendation: Optional[dict[str, Any]] = None
    cache_advice: Optional[dict[str, Any]] = None
    output_budget_advice: Optional[dict[str, Any]] = None
    language_advice: Optional[dict[str, Any]] = None


class ChatCompressRequest(BaseModel):
    messages: list[dict[str, Any]] = Field(..., description="Array de mensagens do chat")
    model: str = Field("gpt-4o", description="Modelo-alvo")
    keep_last_n: int = Field(3, description="Número de mensagens recentes mantidas intactas")
    level: CompressionLevel = Field(CompressionLevel.LIGHT, description="Nível de compressão")


class ChatCompressResponse(BaseModel):
    messages: list[dict[str, Any]]
    total_tokens_before: int
    total_tokens_after: int
    tokens_saved: int
    percent_saved: float


class PIIMaskRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto para mascarar PII")


class PIIMaskResponse(BaseModel):
    masked_text: str
    masked_data: dict[str, str]
    pii_found_count: int


class InjectionCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto do prompt a ser analisado")


class InjectionCheckResponse(BaseModel):
    risk_score: float
    risk_level: str
    detected_threats: list[str]


class CompressibilityRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto do prompt")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


async def _run_optimization(req: OptimizeRequest) -> OptimizeResponse:
    try:
        input_text = req.text
        pii_map = None

        if req.mask_pii_data:
            pii_res = mask_pii(input_text)
            input_text = pii_res.text
            pii_map = pii_res.masked_data

        result = optimize(
            text=input_text,
            model=req.model,
            level=req.level,
            semantic=req.semantic,
            strip_emojis=req.strip_emojis,
            strip_code=req.strip_code,
            minify_json_xml=req.minify_json_xml,
            enable_llm_insights=req.enable_llm_insights,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro interno: {exc}")

    d = result.to_dict()
    return OptimizeResponse(
        original=TextWithMetrics(**d["original"]),
        optimized=TextWithMetrics(**d["optimized"]),
        savings=SavingsMetrics(**d["savings"]),
        quality=QualityMetrics(**d.get("quality", {"semantic_similarity_score": 1.0})),
        diff=d["diff"],
        warnings=d["warnings"],
        rules_applied=d["rules_applied"],
        pii_masked_data=pii_map,
        model_recommendation=d.get("model_recommendation"),
        cache_advice=d.get("cache_advice"),
        output_budget_advice=d.get("output_budget_advice"),
        language_advice=d.get("language_advice"),
    )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_endpoint(req: OptimizeRequest) -> OptimizeResponse:
    return await _run_optimization(req)


@legacy_router.post("/optimize", response_model=OptimizeResponse, include_in_schema=False)
async def optimize_legacy_endpoint(req: OptimizeRequest) -> OptimizeResponse:
    return await _run_optimization(req)


@router.post("/chat/compress", response_model=ChatCompressResponse)
async def compress_chat_endpoint(req: ChatCompressRequest) -> ChatCompressResponse:
    try:
        res = compress_chat_history(
            messages=req.messages,
            model=req.model,
            keep_last_n=req.keep_last_n,
            level=req.level,
        )
        return ChatCompressResponse(**res)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao comprimir chat: {exc}")


@router.post("/pii/mask", response_model=PIIMaskResponse)
async def mask_pii_endpoint(req: PIIMaskRequest) -> PIIMaskResponse:
    res = mask_pii(req.text)
    return PIIMaskResponse(
        masked_text=res.text,
        masked_data=res.masked_data,
        pii_found_count=res.pii_found_count,
    )


@router.post("/injection/check", response_model=InjectionCheckResponse)
async def check_injection_endpoint(req: InjectionCheckRequest) -> InjectionCheckResponse:
    res = check_prompt_injection(req.text)
    return InjectionCheckResponse(
        risk_score=res.risk_score,
        risk_level=res.risk_level,
        detected_threats=res.detected_threats,
    )


@router.post("/compressibility")
async def check_compressibility_endpoint(req: CompressibilityRequest) -> dict[str, Any]:
    return analyze_compressibility(req.text)


@router.post("/admin/reload-prices")
async def reload_prices_endpoint() -> dict[str, str]:
    try:
        load_custom_prices()
        return {"status": "success", "message": "Preços recarregados com sucesso."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao recarregar preços: {exc}")
