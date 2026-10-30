#!/usr/bin/env python3
"""
👻 GhostShell - Local AI Terminal Companion
Runs 100% locally with Ollama. No cloud, no data leaks.
"""

import os
import re
from pathlib import Path

import ollama
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

app = typer.Typer(
    name="ghostshell",
    help="👻 GhostShell - Local AI Terminal Companion",
    add_completion=False,
)
console = Console()

DEFAULT_MODEL = os.getenv("GHOSTSHELL_MODEL", "gemma:2b")

# Dangerous patterns — pehle se check ho jayenge
DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+/\s*$", "🚨 DANGER: Deleting from root filesystem!"),
    (r"rm\s+-rf\s+/\w+(?!tmp)", "🚨 DANGER: Deleting top-level system directory!"),
    (r"rm\s+-rf\s+\*", "🚨 DANGER: Deleting ALL files in current directory!"),
    (r"chmod\s+777", "⚠️  WARNING: chmod 777 gives full permissions to everyone!"),
    (r"curl[^|]*\|\s*(bash|sh)", "🚨 DANGER: Piping remote content to shell!"),
    (r"wget[^|]*\|\s*(bash|sh)", "🚨 DANGER: Piping remote content to shell!"),
    (r"dd\s+if=.*of=/dev/", "🚨 DANGER: Writing directly to a device!"),
    (r":\(\)\{.*\};:", "🚨 DANGER: Fork bomb detected!"),
    (r">\s*/dev/sd[a-z]", "🚨 DANGER: Overwriting a disk device!"),
    (r"mv\s+.*\s+/dev/null", "⚠️  WARNING: Moving files to /dev/null (permanent loss!)"),
    (r"--no-preserve-root", "🚨 DANGER: --no-preserve-root bypasses safety!"),
]


# ---------- Helper functions ----------

def check_ollama() -> bool:
    """Ollama chal raha hai ya nahi"""
    try:
        ollama.list()
        return True
    except Exception:
        console.print(Panel(
            "[red]Ollama नहीं चल रहा है![/red]\n\n"
            "1. Ollama install करें: [cyan]https://ollama.com/download[/cyan]\n"
            "2. Terminal में चलाएं: [cyan]ollama serve[/cyan]\n"
            "3. Model download करें: [cyan]ollama pull gemma:2b[/cyan]",
            title="❌ Setup Required",
            border_style="red",
        ))
        return False


def check_model(model: str) -> bool:
    """Model available hai ya nahi"""
    try:
        models = ollama.list()
        model_list = models.get("models", []) if isinstance(models, dict) else getattr(models, "models", [])
        
        # New ollama library uses object properties (m.model), old uses dictionary (m['name'])
        available = []
        for m in model_list:
            if isinstance(m, dict):
                name = m.get("model") or m.get("name", "")
            else:
                name = getattr(m, "model", getattr(m, "name", ""))
            available.append(name)

        base = model.split(":")[0]
        if not any(base in m for m in available):
            console.print(
                f"[yellow]⚠️  Model '{model}' नहीं मिला। Download कर रहे हैं...[/yellow]"
            )
            ollama.pull(model)
        return True
    except Exception as e:
        console.print(f"[red]❌ Model check failed: {e}[/red]")
        return False


def ask_ai(prompt: str, model: str) -> str:
    """AI se jawab lo"""
    try:
        with console.status("[bold cyan]👻 GhostShell सोच रहा है...[/bold cyan]"):
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
        if isinstance(response, dict):
            return response.get("message", {}).get("content", "")
        return getattr(getattr(response, "message", None), "content", "")
    except Exception as e:
        console.print(f"[red]❌ AI error: {e}[/red]")
        return ""


def safety_scan(command: str) -> list:
    """Dangerous patterns dhundho"""
    warnings = []
    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            warnings.append(message)
    return warnings


def show_warnings(warnings: list):
    if warnings:
        body = "\n".join(warnings)
        console.print(Panel(body, title="🔍 Safety Scan", border_style="yellow"))


# ---------- Commands ----------

@app.command()
def explain(
    command: str = typer.Argument(..., help="Shell command jo samajhni hai"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Ollama model"),
    safety: bool = typer.Option(True, "--safety/--no-safety", help="Safety scan karo"),
):
    """किसी भी shell command को simple भाषा में समझाओ"""
    if not check_ollama() or not check_model(model):
        raise typer.Exit(1)

    if safety:
        show_warnings(safety_scan(command))

    prompt = f"""You are an expert Linux/Unix developer helping a beginner.
Explain this shell command in simple, clear terms.

Command: {command}

Answer in this exact format:
1. **What it does** (one sentence)
2. **Breaking down the parts** (each flag/argument)
3. **Risks or warnings** (if any)
4. **Safer alternative** (if applicable)

Be concise but complete. Use plain language. No fluff."""

    console.print(Panel(f"[cyan]{command}[/cyan]", title="📖 Explaining", border_style="cyan"))
    answer = ask_ai(prompt, model)
    if answer:
        console.print()
        console.print(Markdown(answer))
        console.print()


@app.command()
def diagnose(
    logfile: str = typer.Argument(..., help="Error log file ka path"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m"),
):
    """Error log को analyze करके fix suggest karo"""
    if not check_ollama() or not check_model(model):
        raise typer.Exit(1)

    path = Path(logfile)
    if not path.exists():
        console.print(f"[red]❌ File नहीं मिली: {logfile}[/red]")
        raise typer.Exit(1)

    try:
        content = path.read_text(errors="ignore")
    except Exception as e:
        console.print(f"[red]❌ File पढ़ने में error: {e}[/red]")
        raise typer.Exit(1)

    if len(content) > 5000:
        content = "...(truncated)...\n" + content[-5000:]

    prompt = f"""You are a debugging expert. Analyze this error log
and give a concise diagnosis with clear fixes.

Error log:
{content}

Respond in this exact format:
1. **What went wrong** (1-2 sentences)
2. **Likely cause**
3. **How to fix it** (numbered steps)
4. **How to prevent this** (1 line)"""

    console.print(Panel(f"[cyan]{logfile}[/cyan]", title="📖 Analyzing", border_style="cyan"))
    answer = ask_ai(prompt, model)
    if answer:
        console.print()
        console.print(Markdown(answer))
        console.print()


@app.command()
def safety(
    command: str = typer.Argument(..., help="Command jo check karni hai"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m"),
):
    """Command safe hai ya nahi batao"""
    if not check_ollama() or not check_model(model):
        raise typer.Exit(1)

    show_warnings(safety_scan(command))

    prompt = f"""Analyze the safety of this shell command for a user's machine.
Command: {command}

Respond in this exact format:
- **Risk Level**: LOW / MEDIUM / HIGH / CRITICAL
- **What it does**: 1-2 sentences
- **Main risks**: bullet list (or "None" if safe)
- **Safer version**: alternative command if applicable"""

    answer = ask_ai(prompt, model)
    if answer:
        console.print()
        console.print(Markdown(answer))
        console.print()


@app.command()
def chat(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m"),
):
    """Interactive chat mode — kuch bhi poochho"""
    if not check_ollama() or not check_model(model):
        raise typer.Exit(1)

    console.print(Panel(
        "👻 GhostShell Chat Mode\n"
        "Kuch bhi poochho. 'exit' ya Ctrl+C se band karein.",
        border_style="cyan",
    ))

    history = []
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Bye! 👻[/yellow]")
            break

        if user_input.strip().lower() in {"exit", "quit", "bye"}:
            console.print("[yellow]Bye! 👻[/yellow]")
            break
        if not user_input.strip():
            continue

        history.append({"role": "user", "content": user_input})
        try:
            with console.status("[cyan]👻 thinking...[/cyan]"):
                response = ollama.chat(model=model, messages=history)
            
            if isinstance(response, dict):
                reply = response.get("message", {}).get("content", "")
            else:
                reply = getattr(getattr(response, "message", None), "content", "")
                
            history.append({"role": "assistant", "content": reply})
            console.print(f"[green]👻 GhostShell:[/green] {reply}\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def version():
    """Version dikhao"""
    console.print("[cyan]👻 GhostShell v1.0.0[/cyan]")
    console.print("Local AI terminal companion — privacy-first")


if __name__ == "__main__":
    app()