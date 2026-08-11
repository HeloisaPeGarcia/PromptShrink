"""
FastAPI application — PromptShrink API (v1 + legacy endpoints + Web Dashboard).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.optimize import router as optimize_router, legacy_router
from api.routes.health import router as health_router
from api.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="PromptShrink API",
    description="Pré-processador de prompts de IA — reduz tokens, economiza dinheiro.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(optimize_router)
app.include_router(legacy_router)
app.include_router(dashboard_router)
