#!/usr/bin/env python3
import typer
import asyncio
from pathlib import Path
import importlib.metadata
import uvicorn
from typing import Optional

app = typer.Typer(no_args_is_help=True)

def get_version():
    try:
        return importlib.metadata.version("vilcos")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"

@app.command()
def version():
    """Show the vilcos version."""
    typer.echo(f"Vilcos version: {get_version()}")

@app.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: Optional[int] = None
):
    """Run the development server."""
    typer.echo(f"Starting vilcos server on http://{host}:{port}")
    uvicorn.run(
        "vilcos.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers
    )

@app.command()
def init_db():
    """Initialize the database and create tables."""
    from vilcos.database import create_tables

    async def _init_db():
        await create_tables()
        typer.echo("Database tables created successfully.")

    asyncio.run(_init_db())

@app.command()
def shell():
    """Launch an interactive IPython shell with the database context."""
    try:
        from IPython import embed
    except ImportError:
        typer.echo("IPython is not installed. Please install it with 'pip install ipython'.")
        return
    
    embed()

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()
