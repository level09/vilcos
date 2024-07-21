from flask import request, Blueprint, send_from_directory
from flask.templating import render_template

public = Blueprint('public',__name__, static_folder='../static')

@public.route('/')
def index():
    return render_template('index.html')


@public.route('/robots.txt')
def static_from_root():
    return send_from_directory(public.static_folder, request.path[1:])