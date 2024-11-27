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
    from vilcos.db import engine, Base
    from vilcos.models import Role  # Import models to register them with Base

    async def _init_db():
        try:
            console.print(f"[bold green]Connecting to database at [underline]{engine.url}[/underline][/bold green]")
            
            # First, create all tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                console.print("[bold green]Tables created successfully[/bold green]")
            
            # Then initialize default roles using AsyncSessionLocal
            from vilcos.db import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                # Check if roles already exist
                from sqlalchemy.future import select
                result = await session.execute(select(Role).where(Role.name == "admin"))
                if not result.scalar_one_or_none():
                    default_roles = [
                        Role(name="admin", description="Administrator with full access"),
                        Role(name="user", description="Regular user with standard access")
                    ]
                    session.add_all(default_roles)
                    await session.commit()
                    console.print("[bold green]Default roles created successfully[/bold green]")
                else:
                    console.print("[yellow]Default roles already exist[/yellow]")
            
            console.print("[bold green]Database initialization completed successfully[/bold green]")
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
