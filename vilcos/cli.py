#!/usr/bin/env python3
import typer
import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from vilcos.database import create_tables, get_db, manage_db
from vilcos.models import Table, TimeSlot, Reservation
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from vilcos.config import settings  # Ensure this import is correct based on your project structure

app = typer.Typer(no_args_is_help=True)


@app.command()
def init_db():
    """Initialize the database and create tables."""
    
    async def _init_db():
        async with manage_db(app):
            typer.echo("Database initialized and tables created.")

    asyncio.run(_init_db())


@app.command()
def setup_initial_data():
    """Create initial restaurant data if it doesn't exist."""

    async def _create_data():
        async for session in get_db():
            result = await session.execute(select(Table))
            existing_data = result.scalars().all()

            if not existing_data:
                for i in range(1, 21):
                    new_item = Table(
                        table_number=i,
                        capacity=4,
                        location="Main Area"
                    )
                    session.add(new_item)

                await session.commit()
                typer.echo("Initial restaurant data created.")
            else:
                typer.echo("Initial data already exists. Skipping setup.")

    asyncio.run(_create_data())


@app.command()
def shell():
    """Launch an interactive IPython shell with the database context."""
    try:
        from IPython import embed
    except ImportError:
        typer.echo("IPython is not installed. Please install it with 'pip install ipython'.")
        return

    # Correct the database URL for synchronous operations
    SQLALCHEMY_DATABASE_URL = settings.database_url.replace(
        'postgresql+asyncpg://', 'postgresql://'
    ) if 'postgresql+asyncpg://' in settings.database_url else settings.database_url

    if not SQLALCHEMY_DATABASE_URL:
        typer.echo("SQLALCHEMY_DATABASE_URL is not defined. Please check your database configuration.")
        return

    # Create the engine and session factory for synchronous operations
    engine = create_engine(SQLALCHEMY_DATABASE_URL)  # Use psycopg2 for sync
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create a dictionary of the context you want to have in the shell
    context = {
        'Table': Table,
        'TimeSlot': TimeSlot,
        'Reservation': Reservation,
        'SessionLocal': SessionLocal,  # Add the session factory to the context
    }

    # Start the IPython shell with the context
    embed(user_ns=context)


if __name__ == "__main__":
    app()
