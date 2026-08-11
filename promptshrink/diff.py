"""
Diff visual e painéis de LLM Engineering no terminal usando Rich.
"""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

if TYPE_CHECKING:
    from promptshrink.models import OptimizationResult


def _make_diff_lines(original: str, optimized: str) -> list[str]:
    """Gera linhas de unified diff entre original e otimizado."""
    orig_lines = original.splitlines(keepends=True)
    opt_lines = optimized.splitlines(keepends=True)
    return list(
        difflib.unified_diff(
            orig_lines,
            opt_lines,
            fromfile="original",
            tofile="otimizado",
            lineterm="",
        )
    )


def render_diff(result: "OptimizationResult", console: Console | None = None) -> None:
    """
    Renderiza o diff, métricas e análises de LLM Engineering no terminal com Rich.
    """
    if console is None:
        console = Console()

    m = result.metrics

    # Painel de métricas
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="dim")
    table.add_column("Antes", justify="right")
    table.add_column("Depois", justify="right")
    table.add_column("Economia / Qualidade", justify="right", style="green")

    token_savings_str = (
        f"[green]-{m.tokens_saved} ({m.percent_saved}%)[/green]"
        if m.tokens_saved > 0
        else "[yellow]0[/yellow]"
    )
    cost_savings_str = (
        f"[green]-${m.cost_saved_usd:.6f}[/green]"
        if m.cost_saved_usd > 0
        else "[yellow]$0[/yellow]"
    )
    quality_str = f"[bold green]{int(m.semantic_similarity_score * 100)}% Retenção[/bold green]"

    table.add_row(
        "Tokens (Input)",
        str(m.tokens_before),
        str(m.tokens_after),
        token_savings_str,
    )
    table.add_row(
        "Custo (Input)",
        f"${m.cost_before_usd:.6f}",
        f"${m.cost_after_usd:.6f}",
        cost_savings_str,
    )
    table.add_row("Fidelidade Semântica", "-", "-", quality_str)
    table.add_row("Modelo", m.model, "", "")

    console.print(Panel(table, title="📊 Métricas de Otimização", border_style="cyan"))

    # Model Routing Recommendation
    if result.model_recommendation:
        mr = result.model_recommendation
        rec_text = (
            f"[bold yellow]Sugestão de Modelo:[/bold yellow] Trocar '{mr.current_model}' → [bold green]'{mr.suggested_model}'[/bold green]\n"
            f"[dim]Complexidade detectada:[/dim] {mr.complexity_level.upper()}\n"
            f"[dim]Razão:[/dim] {mr.reasoning}\n"
            f"[bold green]Economia Potencial: -{mr.percent_cheaper}% (-${mr.potential_cost_savings_usd:.6f})[/bold green]"
        )
        console.print(Panel(rec_text, title="🎯 Model Router Advisor", border_style="yellow"))

    # Output Budget Advice
    if result.output_budget_advice:
        ob = result.output_budget_advice
        budget_text = (
            f"[bold cyan]Intenção Detectada:[/bold cyan] {ob.intent_detected}\n"
            f"[bold yellow]Restrição de Resposta Sugerida:[/bold yellow] \"{ob.suggested_constraint}\"\n"
            f"[dim]Tokens adicionados no prompt:[/dim] +{ob.prompt_tokens_added} | "
            f"[dim]Tokens economizados na resposta:[/dim] ~{ob.est_output_tokens_saved}\n"
            f"[bold green]Economia Líquida Estimada: -${ob.net_cost_savings_usd:.6f} (ROI: {ob.roi_multiplier}x)[/bold green]"
        )
        console.print(Panel(budget_text, title="💡 Output Budget Advisor (ROI Resposta)", border_style="magenta"))

    # Prompt Caching Advice
    if result.cache_advice and result.cache_advice.is_cacheable:
        ca = result.cache_advice
        cache_text = (
            f"[bold green]Prefixo Cacheável Detectado:[/bold green] {ca.prefix_tokens} tokens fixos\n"
            f"[dim]{ca.explanation}[/dim]\n"
            f"[bold green]Economia por Chamada em Cache Hit: -${ca.estimated_cache_savings_usd:.6f}[/bold green]"
        )
        console.print(Panel(cache_text, title="🔄 Prompt Caching Advisor", border_style="green"))

    # Language Optimization Advice
    if result.language_advice and result.language_advice.english_instruction_prompt:
        la = result.language_advice
        lang_text = (
            f"[bold cyan]Idioma Detectado:[/bold cyan] {la.detected_language.upper()}\n"
            f"[dim]Instrução em Inglês gera maior densidade de tokens (BPE).[/dim]\n"
            f"[bold green]Economia de Densidade: -{la.tokens_saved} tokens (-{la.percent_saved}%)[/bold green]"
        )
        console.print(Panel(lang_text, title="🌐 Language Density Router", border_style="blue"))

    # Warnings
    if result.warnings:
        for w in result.warnings:
            console.print(f"[yellow]⚠[/yellow]  {w}")

    # Diff visual
    if result.diff_lines:
        diff_text = Text()
        for line in result.diff_lines:
            if line.startswith("+++") or line.startswith("---"):
                diff_text.append(line + "\n", style="bold white")
            elif line.startswith("@@"):
                diff_text.append(line + "\n", style="cyan")
            elif line.startswith("+"):
                diff_text.append(line + "\n", style="green")
            elif line.startswith("-"):
                diff_text.append(line + "\n", style="red strike")
            else:
                diff_text.append(line + "\n", style="dim")

        console.print(Panel(diff_text, title="🔍 Diff (− removido | + mantido)", border_style="blue"))
    else:
        console.print("[dim]Nenhuma alteração foi feita no texto.[/dim]")

    # Regras aplicadas
    if result.rules_applied:
        rules_str = ", ".join(result.rules_applied)
        console.print(f"\n[dim]Regras e transformações aplicadas:[/dim] {rules_str}\n")


def make_diff_lines(original: str, optimized: str) -> list[str]:
    """Exposta para uso externo (API)."""
    return _make_diff_lines(original, optimized)
