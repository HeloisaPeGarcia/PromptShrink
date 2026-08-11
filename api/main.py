"""
FastAPI application — PromptShrink API (v1).
"""

from __future__ import annotations

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from api.routes.optimize import router as optimize_router
from api.routes.health import router as health_router

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
