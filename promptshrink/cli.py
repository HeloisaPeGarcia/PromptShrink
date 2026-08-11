"""
CLI do PromptShrink — interface de console com Rich e Typer.

Uso:
    promptshrink optimize --model gpt-4o --level moderate
    echo "meu prompt" | promptshrink optimize --model gpt-4o
    promptshrink optimize --from-file prompt.txt --json
    promptshrink models
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich import box

from promptshrink.models import CompressionLevel, ModelTarget
from promptshrink.optimizer import optimize
from promptshrink.cost_estimator import list_models
from promptshrink.diff import render_diff
from promptshrink.compressibility import analyze_compressibility

app = typer.Typer(
    name="promptshrink",
    help="🗜️  PromptShrink — reduza tokens, economize dinheiro com seus prompts de IA.",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console(stderr=False)
err_console = Console(stderr=True)


def _read_input(from_file: Optional[Path]) -> str:
    """Lê o texto do prompt de arquivo ou stdin."""
    if from_file:
        if not from_file.exists():
            err_console.print(f"[red]Erro:[/red] arquivo não encontrado: {from_file}")
            raise typer.Exit(1)
        return from_file.read_text(encoding="utf-8")

    if sys.stdin.isatty():
        console.print(
            "[cyan]Cole seu prompt abaixo. Pressione[/cyan] [bold]Ctrl+D[/bold] "
            "[cyan](Linux/Mac) ou[/cyan] [bold]Ctrl+Z + Enter[/bold] [cyan](Windows) para finalizar:[/cyan]\n"
        )
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines)

    return sys.stdin.read()


def _copy_to_clipboard(text: str) -> bool:
    """Tenta copiar texto para a área de transferência."""
    try:
        import pyperclip  # type: ignore
        pyperclip.copy(text)
        return True
    except Exception:
        return False


@app.command("optimize")
def cmd_optimize(
    model: str = typer.Option(
        "gpt-4o",
        "--model", "-m",
        help="Modelo-alvo: gpt-4o, gpt-4o-mini, claude-3-5-sonnet, gemini-1.5-pro, ...",
    ),
    level: CompressionLevel = typer.Option(
        CompressionLevel.LIGHT,
        "--level", "-l",
        help="Nível de compressão: none / light / moderate / aggressive",
    ),
    no_semantic: bool = typer.Option(
        False,
        "--no-semantic",
        help="Desativa compressão semântica (só sanitização Nível 1)",
    ),
    output_json: bool = typer.Option(
        False,
        "--json",
        help="Output em JSON (sem cores, para pipes/scripts)",
    ),
    from_file: Optional[Path] = typer.Option(
        None,
        "--from-file", "-f",
        help="Lê prompt de arquivo em vez de stdin",
    ),
    save_to_file: Optional[Path] = typer.Option(
        None,
        "--save-to-file", "-s",
        help="Salva o resultado otimizado diretamente em um arquivo",
    ),
    apply_language: bool = typer.Option(
        False,
        "--apply-language",
        help="Aplica a tradução de instrução para inglês se gerar economia de tokens",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Executa apenas pré-análise de potencial sem alterar o texto",
    ),
    no_copy: bool = typer.Option(
        False,
        "--no-copy",
        help="Não copia resultado para clipboard",
    ),
    strip_emojis: bool = typer.Option(
        False,
        "--strip-emojis",
        help="Remove emojis decorativos",
    ),
) -> None:
    """
    [bold cyan]Otimiza um prompt[/bold cyan] — sanitiza, comprime e calcula economia de tokens.
    """
    try:
        text = _read_input(from_file)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Cancelado.[/yellow]")
        raise typer.Exit(0)

    if not text.strip():
        err_console.print("[red]Erro:[/red] texto vazio.")
        raise typer.Exit(1)

    if dry_run:
        comp_info = analyze_compressibility(text)
        console.print(Panel(
            f"[bold cyan]Score de Compressibilidade:[/bold cyan] {comp_info['compressibility_score']*100}%\n"
            f"[bold yellow]Categoria:[/bold yellow] {comp_info['potential_savings_category']}\n"
            f"[dim]Motivos:[/dim] {', '.join(comp_info['reasons'])}",
            title="🔍 Dry Run — Pré-Análise de Potencial",
            border_style="cyan"
        ))
        raise typer.Exit(0)

    semantic = not no_semantic

    if not output_json:
        with console.status("[bold cyan]Otimizando prompt…[/bold cyan]"):
            result = optimize(
                text=text,
                model=model,
                level=level,
                semantic=semantic,
                strip_emojis=strip_emojis,
            )
    else:
        result = optimize(
            text=text,
            model=model,
            level=level,
            semantic=semantic,
            strip_emojis=strip_emojis,
        )

    final_text = result.optimized_text
    if apply_language and result.language_advice and result.language_advice.english_instruction_prompt:
        final_text = result.language_advice.english_instruction_prompt

    if save_to_file:
        save_to_file.write_text(final_text, encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] Resultado salvo em: {save_to_file}")

    if output_json:
        d = result.to_dict()
        d["optimized"]["text"] = final_text
        print(json.dumps(d, ensure_ascii=False, indent=2))
        raise typer.Exit(0)

    console.print()
    render_diff(result, console=console)

    console.print(
        Panel(
            final_text,
            title="✅ Prompt Otimizado",
            border_style="green",
            padding=(1, 2),
        )
    )

    m = result.metrics
    if m.tokens_saved <= 0:
        console.print("[dim]Nenhuma redução significativa encontrada.[/dim]")
        raise typer.Exit(0)

    console.print()
    apply = Confirm.ask(
        f"[green]Aplicar?[/green] "
        f"([bold green]-{m.tokens_saved} tokens / -{m.percent_saved}%[/bold green])"
    )

    if apply:
        if not no_copy:
            copied = _copy_to_clipboard(final_text)
            if copied:
                console.print("[green]✓[/green] Copiado para a área de transferência!")
            else:
                console.print(
                    "[yellow]⚠[/yellow] Clipboard indisponível. "
                    "Texto otimizado abaixo:\n"
                )
                print(final_text)
        else:
            print(final_text)
    else:
        console.print("[dim]Prompt original mantido.[/dim]")


@app.command("models")
def cmd_models() -> None:
    """Lista os modelos suportados com seus preços por 1M tokens."""
    table = Table(
        title="📋 Modelos suportados",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Modelo", style="white")
    table.add_column("Input ($/1M tokens)", justify="right", style="green")
    table.add_column("Output ($/1M tokens)", justify="right", style="yellow")

    for m in list_models():
        table.add_row(
            m["model"],
            f"${m['input_per_1m_usd']:.3f}",
            f"${m['output_per_1m_usd']:.3f}",
        )

    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
