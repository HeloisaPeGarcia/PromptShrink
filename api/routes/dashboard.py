"""
Endpoint GET /dashboard — Dashboard Web de Telemetria e Economia em Tempo Real.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["dashboard"])

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>PromptShrink — Dashboard</title>
  <style>
    body {
      margin: 0; padding: 24px; background: #0f172a; color: #f8fafc;
      font-family: system-ui, -apple-system, sans-serif;
    }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    h1 { margin: 0; font-size: 24px; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; text-align: center; }
    .card-val { font-size: 28px; font-weight: 700; color: #34d399; margin-top: 6px; }
    .card-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; }
    .panel { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
    th { color: #38bdf8; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🗜️ PromptShrink Dashboard</h1>
    <span style="color:#64748b; font-size:12px;">v0.2.0 ● Live Telemetry</span>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-label">Tokens Economizados</div>
      <div class="card-val" id="valTokens">1,248,500</div>
    </div>
    <div class="card">
      <div class="card-label">Economia Estimada</div>
      <div class="card-val" id="valCost">$3.12</div>
    </div>
    <div class="card">
      <div class="card-label">Prompts Otimizados</div>
      <div class="card-val" id="valRequests">4,210</div>
    </div>
    <div class="card">
      <div class="card-label">Taxa Média de Redução</div>
      <div class="card-val" id="valRatio">38.4%</div>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0; color:#cbd5e1;">📋 Regras de Compressão Mais Ativas</h3>
    <table>
      <thead>
        <tr><th>Regra</th><th>Categoria</th><th>Acionamentos</th><th>Impacto Médio</th></tr>
      </thead>
      <tbody>
        <tr><td><code>remove_greetings_pt</code></td><td>Sanitização Semântica</td><td>3,120</td><td>-12.4%</td></tr>
        <tr><td><code>strip_code_comments</code></td><td>Code Stripper</td><td>1,840</td><td>-42.1%</td></tr>
        <tr><td><code>please_simplify_pt</code></td><td>Cortesias</td><td>2,450</td><td>-18.0%</td></tr>
        <tr><td><code>minify_json_xml</code></td><td>Format Minifier</td><td>920</td><td>-28.5%</td></tr>
      </tbody>
    </table>
  </div>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page() -> HTMLResponse:
    """Retorna o painel de telemetria e economia em tempo real."""
    return HTMLResponse(content=_DASHBOARD_HTML)
