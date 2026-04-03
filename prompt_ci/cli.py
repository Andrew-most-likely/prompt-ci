from pathlib import Path

import typer
from rich.console import Console

from .config import load_config
from .runner import build_prompt, run_prompt
from .similarity import score_similarity
from .storage import load_golden, save_golden

app = typer.Typer(help="Prompt Regression CI -- catch when your AI stops behaving as expected.")
console = Console()

INIT_CONFIG = """\
# prompt-ci.yaml
provider: anthropic          # anthropic | openai | mock (mock needs no API key, for testing)
model: claude-haiku-4-5-20251001
threshold: 0.80              # 0.0-1.0, fail if similarity drops below this
golden_dir: .golden          # where recorded outputs are stored

tests:
  - name: summarize_concise
    prompt: "Summarize the following in exactly 3 bullet points, be concise: {{input}}"
    input: |
      Artificial intelligence is transforming industries worldwide.
      Companies are investing billions in AI research and development.
      The technology raises questions about jobs, privacy, and ethics.
    threshold: 0.85          # optional per-test override

  - name: extract_sentiment
    prompt: "What is the sentiment of this text? Reply with one word: positive, negative, or neutral."
    input: "I absolutely love this product, it changed my life!"
"""


@app.command()
def init():
    """Create a starter prompt-ci.yaml config."""
    p = Path("prompt-ci.yaml")
    if p.exists():
        typer.confirm("prompt-ci.yaml already exists. Overwrite?", abort=True)
    p.write_text(INIT_CONFIG)
    console.print("[green]OK[/green] Created prompt-ci.yaml -- edit your tests and run `prompt-drift record`")


@app.command()
def record(config_path: str = typer.Option("prompt-ci.yaml", "--config", "-c")):
    """Run all prompts and save outputs as golden files."""
    config = load_config(config_path)
    console.print(f"\n[bold]Recording golden outputs[/bold] ({len(config.tests)} tests)\n")

    for test in config.tests:
        with console.status(f"  Running [cyan]{test.name}[/cyan]..."):
            prompt = build_prompt(test)
            output = run_prompt(prompt, config)
            path = save_golden(config.golden_dir, test.name, prompt, output, config.model, config.provider)

        console.print(f"  [green]OK[/green] [cyan]{test.name}[/cyan] -> {path}")
        console.print(f"    [dim]{output[:120].strip()}{'...' if len(output) > 120 else ''}[/dim]\n")

    console.print(f"\n[bold green]Done.[/bold green] Commit your [cyan]{config.golden_dir}/[/cyan] directory to lock these as expected outputs.")


@app.command()
def check(
    config_path: str = typer.Option("prompt-ci.yaml", "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Check current outputs against golden files. Exits 1 if any test fails."""
    config = load_config(config_path)
    console.print(f"\n[bold]Checking prompts[/bold] ({len(config.tests)} tests)\n")

    results = []
    failed = 0

    for test in config.tests:
        threshold = test.threshold if test.threshold is not None else config.threshold
        golden = load_golden(config.golden_dir, test.name)

        if golden is None:
            console.print(f"  [yellow]WARN[/yellow] [cyan]{test.name}[/cyan] -- no golden file, run `prompt-drift record` first")
            results.append((test.name, None, None, threshold, "no-golden"))
            failed += 1
            continue

        with console.status(f"  Checking [cyan]{test.name}[/cyan]..."):
            prompt = build_prompt(test)
            actual = run_prompt(prompt, config)
            score, method = score_similarity(golden["output"], actual, config.provider, config.model)

        passed = score >= threshold
        if not passed:
            failed += 1

        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        console.print(f"  {status} [cyan]{test.name}[/cyan]  score={score:.2f}  threshold={threshold:.2f}  ({method})")

        if verbose or not passed:
            expected_preview = golden['output'][:100].strip()
            actual_preview = actual[:100].strip()
            console.print(f"    [dim]Expected:[/dim] {expected_preview}{'...' if len(golden['output']) > 100 else ''}")
            console.print(f"    [dim]Actual:  [/dim] {actual_preview}{'...' if len(actual) > 100 else ''}")
            console.print()

        results.append((test.name, score, passed, threshold, method))

    _print_summary(results, failed)

    if failed > 0:
        raise typer.Exit(1)


@app.command()
def show(
    test_name: str = typer.Argument(...),
    config_path: str = typer.Option("prompt-ci.yaml", "--config", "-c"),
):
    """Show the stored golden output for a test."""
    config = load_config(config_path)
    golden = load_golden(config.golden_dir, test_name)
    if golden is None:
        console.print(f"[red]No golden file found for '{test_name}'[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold]Golden output for:[/bold] {test_name}")
    console.print(f"Recorded: {golden['recorded_at']}  Model: {golden['model']}\n")
    console.print(golden["output"])


def _print_summary(results, failed):
    total = len(results)
    console.print()
    if failed == 0:
        console.print(f"[bold green]All {total} tests passed.[/bold green]")
    else:
        console.print(f"[bold red]{failed}/{total} tests failed.[/bold red]")


def main():
    app()
