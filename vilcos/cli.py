#!/usr/bin/env python3
import typer
import asyncio
from pathlib import Path
import importlib.metadata
import uvicorn
from typing import Optional
import os
import sys

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
    app_dir: str = typer.Option(".", help="Application directory"),
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: Optional[int] = None,
    app_module: str = typer.Option(None, help="Module path to ASGI app (eg: 'app:app')")
):
    """Run the development server."""
    # Add the current directory to Python path
    cwd = os.getcwd()
    sys.path.insert(0, cwd)
    
    # Validate app directory
    app_path = Path(app_dir).resolve()
    if not app_path.exists():
        typer.echo(f"Error: Directory '{app_dir}' does not exist", err=True)
        raise typer.Exit(1)
    
    # Change to the app directory
    os.chdir(app_path)
    
    # Auto-detect the application module
    if app_module is None:
        if (app_path / "app.py").exists():
            app_module = "app:app"
        elif (app_path / "main.py").exists():
            app_module = "main:app"
        else:
            # Default to vilcos framework app if no local app is found
            app_module = "vilcos.main:app"
            # Add the package directory to Python path for framework mode
            package_dir = str(Path(__file__).parent.parent)
            if package_dir not in sys.path:
                sys.path.insert(0, package_dir)
    
    typer.echo(f"Starting server on http://{host}:{port}")
    typer.echo(f"Application directory: {app_path}")
    typer.echo(f"Using application: {app_module}")
    
    uvicorn.run(
        app_module,
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
