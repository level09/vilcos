from flask import Blueprint
from flask.templating import render_template

portal = Blueprint('portal', __name__, static_folder='../static')

def before_request():
    pass
@portal.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=10800'
    return response


@portal.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

