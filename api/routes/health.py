"""
GET /health — health check e informações básicas do serviço.
GET /models — lista modelos suportados com preços.
"""

from __future__ import annotations

from fastapi import APIRouter

from promptshrink import __version__
from promptshrink.cost_estimator import list_models

router = APIRouter(tags=["infra"])


@router.get("/health")
async def health() -> dict:
    """Verifica se o serviço está operacional."""
    return {
        "status": "ok",
        "service": "promptshrink",
        "version": __version__,
    }


@router.get("/models")
async def models() -> dict:
    """Lista modelos suportados com preços por 1M tokens."""
    return {"models": list_models()}
