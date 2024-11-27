#!/usr/bin/env python3
import typer
import asyncio
import uvicorn
import importlib.metadata
from rich.console import Console

console = Console()

app = typer.Typer(no_args_is_help=True)

from vilcos.models import *

@app.command()
def version():
    """Show the vilcos version."""
    try:
        version = importlib.metadata.version("vilcos")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    typer.echo(f"Vilcos version: {version}")

@app.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
):
    """Run the development server."""
    typer.echo(f"Starting server at http://{host}:{port}")
    
    uvicorn.run(
        "vilcos.app:app",
        host=host,
        port=port,
        reload=reload,
    )

@app.command()
def init_db():
    """Initialize the database."""
    from vilcos.db import init_db as db_init, engine, Base

    async def _init_db():
        try:
            console.print(f"[bold green]Connecting to database at [underline]{engine.url}[/underline][/bold green]")
            await db_init()
            console.print("[bold green]Database initialized successfully.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Database initialization failed: {e}[/bold red]", style="bold red")
            raise typer.Exit(1)

    asyncio.run(_init_db())

@app.command()
def shell():
    """Launch an interactive shell."""
    try:
        from IPython import embed
        embed()
    except ImportError:
        typer.echo("Please install IPython: pip install ipython")
        raise typer.Exit(1)

@app.command()
def show_settings():
    """Print the current settings if in debug mode."""
    from vilcos.config import settings
    if settings.debug:
        typer.echo("Current Settings:")
        for field, value in settings.dict().items():
            typer.echo(f"{field}: {value}")
    else:
        typer.echo("Debug mode is off. Settings are not displayed.")

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()
