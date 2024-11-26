#!/usr/bin/env python3
import typer
import asyncio
import uvicorn
import importlib.metadata

app = typer.Typer(no_args_is_help=True)

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
        "vilcos.main:app",
        host=host,
        port=port,
        reload=reload,
    )

@app.command()
def init_db():
    """Initialize the database."""
    from vilcos.database import create_tables

    async def _init_db():
        try:
            await create_tables()
            typer.echo("Database initialized successfully.")
        except Exception as e:
            typer.echo(f"Database initialization failed: {e}", err=True)
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

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()
