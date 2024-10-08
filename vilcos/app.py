# -*- coding: utf-8 -*-
import inspect

import click
from flask import Flask, render_template

import vilcos.commands as commands
from vilcos.extensions import cache, db, mail, debug_toolbar, session, babel, openai , supabase
from vilcos.portal.views import portal
from vilcos.public.views import public
from vilcos.settings import Config
from vilcos.user.views import bp_user


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    register_blueprints(app)
    register_extensions(app)

    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app, commands)
    return app

def locale_selector():
    return 'en'

def register_extensions(app):
    cache.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    debug_toolbar.init_app(app)
    session.init_app(app)
    babel.init_app(app, locale_selector=locale_selector, default_domain="messages", default_locale="en")
    openai.init_app(app)
    supabase.init_app(app)
    return None


def register_blueprints(app):

    app.register_blueprint(bp_user)
    app.register_blueprint(public)
    app.register_blueprint(portal)
    return None


def register_errorhandlers(app):
    def render_error(error):
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
        }

    app.shell_context_processor(shell_context)


def register_commands(app: Flask, commands_module):
    """
    Automatically register all Click commands in the given module.

    Args:
    - app: Flask application instance to register commands to.
    - commands_module: The module containing Click commands.
    """
    for name, obj in inspect.getmembers(commands_module):
        if isinstance(obj, click.Command):
            app.cli.add_command(obj)
