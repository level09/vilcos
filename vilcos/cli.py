#!/usr/bin/env python3
import typer
import asyncio
import sys
from pathlib import Path
import json
from glob import glob
import re

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from vilcos.database import create_tables, get_db, manage_db
from vilcos.models import DiningTable, TimeSlot, Reservation, Item
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from vilcos.config import settings

app = typer.Typer(no_args_is_help=True)

@app.command()
def init_db():
    """Initialize the database and create tables."""
    
    async def _init_db():
        # Actually create the tables
        await create_tables()
        typer.echo("Database tables created successfully.")

    asyncio.run(_init_db())


@app.command()
def setup_initial_data():
    """Create initial restaurant data if it doesn't exist."""

    async def _create_data():
        async for session in get_db():
            # Check for existing tables
            result = await session.execute(select(DiningTable))
            existing_tables = result.scalars().all()

            if not existing_tables:
                for i in range(1, 21):
                    new_table = DiningTable(
                        table_number=i,
                        capacity=4,
                        location="Main Area"
                    )
                    session.add(new_table)

            # Check for existing time slots
            result = await session.execute(select(TimeSlot))
            existing_time_slots = result.scalars().all()

            if not existing_time_slots:
                durations = [15, 30, 45, 60]  # Preset durations in minutes
                
                for duration in durations:
                    new_slot = TimeSlot(duration=duration)
                    session.add(new_slot)

            # Load items from all JSON files in the directory
            json_files = glob('vilcos/data/*.json')
            all_items = []

            # Fetch existing item numbers to avoid duplicates
            result = await session.execute(select(Item.item_number))
            existing_item_numbers = set(result.scalars().all())
            next_item_number = max(existing_item_numbers, default=0) + 1

            for file_path in json_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data['items']:
                        # Clean and convert price
                        price_str = item['price'].replace(',', '.').strip()
                        match = re.match(r"^\d+(\.\d+)?$", price_str)
                        if match:
                            price = float(match.group())
                        else:
                            typer.echo(f"Invalid price format for item {item['name']}: {price_str}")
                            continue

                        # Assign a unique item number
                        while next_item_number in existing_item_numbers:
                            next_item_number += 1

                        new_item = Item(
                            item_number=next_item_number,
                            name=item['name'],
                            name_korean=item.get('name_korean', ''),
                            description=item.get('description', ''),
                            dietary_info=item.get('dietary_info', ''),
                            price=price
                        )
                        all_items.append(new_item)
                        existing_item_numbers.add(next_item_number)

            # Check for existing items
            result = await session.execute(select(Item))
            existing_items = result.scalars().all()

            if not existing_items:
                session.add_all(all_items)

            await session.commit()
            if not existing_tables or not existing_time_slots or not existing_items:
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
