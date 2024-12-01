#!/usr/bin/env python3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

import typer
import asyncio
import uvicorn
import importlib.metadata
from rich.console import Console
from typing import Dict, Any, Callable
from functools import update_wrapper
from sqlalchemy.future import select
from vilcos.models import *
from vilcos.db import AsyncSession

console = Console()

app = typer.Typer(no_args_is_help=True)

_shell_context_processors: list[Callable[[], Dict[str, Any]]] = []

def shell_context_processor(f: Callable[[], Dict[str, Any]]) -> Callable[[], Dict[str, Any]]:
    """Decorator to register a shell context processor function."""
    _shell_context_processors.append(f)
    return update_wrapper(wrapper=f, wrapped=f)

def get_shell_context() -> Dict[str, Any]:
    """Get the shell context objects."""
    ctx = {
        "User": User,
        "Role": Role,
        "select": select,
        "AsyncSession": AsyncSession,
    }
    
    # Update context with registered processors
    for processor in _shell_context_processors:
        ctx.update(processor())
    
    return ctx

@shell_context_processor
def utility_context() -> Dict[str, Any]:
    """Add utility functions to shell context."""
    async def count_users(session: AsyncSession) -> int:
        result = await session.execute(select(User))
        return len(result.scalars().all())
    
    return {
        "count_users": count_users,
        "APP_VERSION": "1.0.0",
    }

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
def create_admin():
    """Create the first admin user."""
    from vilcos.db import AsyncSessionLocal
    from vilcos.models import User, Role

    async def _create_admin():
        try:
            async with AsyncSessionLocal() as session:
                # First check if admin role exists, if not create it
                result = await session.execute(select(Role).where(Role.name == "admin"))
                admin_role = result.scalar_one_or_none()
                
                if not admin_role:
                    admin_role = Role(name="admin", description="Administrator with full access")
                    session.add(admin_role)
                    await session.commit()
                    await session.refresh(admin_role)
                    console.print("[bold green]Created admin role successfully[/bold green]")
                
                # Check if any admin user exists
                result = await session.execute(
                    select(User).join(user_roles).join(Role).where(Role.name == "admin")
                )
                if result.scalar_one_or_none():
                    console.print("[bold red]An admin user already exists[/bold red]")
                    raise typer.Exit(1)
                
                # Prompt for user details
                email = typer.prompt("Enter admin email")
                username = typer.prompt("Enter admin username")
                password = typer.prompt("Enter admin password", hide_input=True)
                confirm_password = typer.prompt("Confirm admin password", hide_input=True)
                
                if password != confirm_password:
                    console.print("[bold red]Passwords do not match[/bold red]")
                    raise typer.Exit(1)

                # Create the admin user
                admin_user = User(
                    email=email,
                    username=username,
                    password=User.get_password_hash(password),
                    roles=[admin_role]  # Updated to use roles list
                )
                
                session.add(admin_user)
                await session.commit()
                console.print("[bold green]Admin user created successfully[/bold green]")
                
        except Exception as e:
            console.print(f"[bold red]Error creating admin user: {e}[/bold red]")
            raise typer.Exit(1)
    
    asyncio.run(_create_admin())

@app.command()
def shell():
    """Launch an interactive shell."""
    try:
        from IPython import embed
        embed(banner1="Vilcos Shell", user_ns=get_shell_context())
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
