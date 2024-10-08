# -*- coding: utf-8 -*-
"""Click commands."""
import os

import click
from flask.cli import with_appcontext, AppGroup
from rich.console import Console

from vilcos.extensions import db, openai
from rich.progress import Progress, SpinnerColumn

console = Console()


@click.command()
@with_appcontext
def create_db():
    """creates db tables - import your models within commands.py to create the models.
    """
    db.create_all()
    print('Database structure created successfully')









@click.command()
@click.option('--class_name', prompt=True, help='The name of the class')
@click.option('--fields', prompt=True, help='Describe your fields in a natural language')
@with_appcontext
def generate_dashboard(class_name, fields):
    """Generates a dynamic dashboard template for a specified class and fields."""
    # Parse fields input into a list of dictionaries

    sample = open('enferno/templates/core/dashboard.jinja2').read()

    with Progress(SpinnerColumn(), "[progress.description]{task.description}") as progress:
        task = progress.add_task("[cyan]Generating dashboard...", total=None)  # total=None for indefinite tasks

        # Simulate progress
        progress.update(task, advance=30)  # Start the task with some progress

        response = openai.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    Generate an jinja template by copying exactly the following SAMPLE,
                    Note the delimiters being used, you will need to replace project and their attributes with the 
                    following class name and fields,
                    class name: {class_name}
                    Fields: {fields}
                    Sample: {sample} 
                     no yap, just output code
                    """
                },
                {
                    "role": "user",
                    "content": f"The class name is {class_name}  and fields are describe here: {fields}"
                },

            ],
            temperature=0,
            max_tokens=4096,

            # response_format={"type": "json_object"}
        )
        progress.remove_task(task)  # Remove or complete the task once the API call is done

        generated_code = response.choices[0].message.content

    # Print the rendered template with ASCII borders
    console.print(generated_code)




@click.command()
@click.option('--class_name', prompt=True, help='The name of the class')
@click.option('--fields', prompt=True, help='Describe your fields in a natural language')
@with_appcontext
def generate_api(class_name, fields):
    """Generates Flask view functions for API endpoints of a specified class."""

    sample = open('enferno/templates/core/api.jinja2').read()

    with Progress(SpinnerColumn(), "[progress.description]{task.description}") as progress:
        task = progress.add_task("[cyan]Generating API Endpoints ...", total=None)  # total=None for indefinite tasks

        response = openai.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""Generate Flask Endpoints by copying and modifying the following sample,
                     you will need to replace project and adapt the attributes with the given class name and fields,
                        sample: {sample}
                      no yap, don't import libs,  just output code
                    """
                },
                {
                    "role": "user",
                    "content": f"The class name is {class_name}  and fields are describe here: {fields}"
                },

            ],
            temperature=0,
            max_tokens=4096,

            # response_format={"type": "json_object"}
        )

    # Load and render the API views template
    progress.remove_task(task)  # Remove or complete the task once the API call is done

    generated_code = response.choices[0].message.content
    console.print(generated_code)



import click
from jinja2 import Environment, FileSystemLoader, select_autoescape


@click.command()
@click.option('--class_name', prompt=True, help='The name of the class')
@click.option('--fields', prompt=True, help='Describe your fields in a natural language')
def generate_model(class_name, fields):
    """Generates a Flask model class using OpenAI."""
    # Adjust the parsing to accommodate the new format

    sample = open('enferno/templates/core/model.jinja2').read()

    with Progress(SpinnerColumn(), "[progress.description]{task.description}") as progress:
        task = progress.add_task("[cyan]Generating SqlAlchemy Model ...", total=None)  # total=None for indefinite tasks

        response = openai.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"Generate an Flask-SQLAlchemy model class including from_json and to_dict methods, dont import anything, use the following as a sample \n {sample}, no yap, just output code"
                },
                {
                    "role": "user",
                    "content": f"The class name is {class_name}  and fields are describe here: {fields}"
                },

            ],
            temperature=0,
            max_tokens=1024,

            # response_format={"type": "json_object"}
        )
        progress.remove_task(task)  # Remove or complete the task once the API call is done

        generated_code = response.choices[0].message.content
        console.print(generated_code)


# Translations Management
i18n_cli = AppGroup("translate", short_help="commands to help with translation management")


@i18n_cli.command()
@click.argument('lang')
def init(lang):
    if os.system(f'pybabel init -i messages.pot -d enferno/translations -l {lang}'):
        raise RuntimeError("Init command failed")

@i18n_cli.command()
def extract():
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("Extract command failed")


@i18n_cli.command()
def update():
    if os.system("pybabel update -i messages.pot -d enferno/translations"):
        raise RuntimeError("Update command failed")


@i18n_cli.command()
def compile():
    if os.system("pybabel compile -d enferno/translations"):
        raise RuntimeError("Compile command failed")