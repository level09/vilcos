from flask import Blueprint
from flask.templating import render_template
from enferno.user.views import login_required
portal = Blueprint('portal', __name__, static_folder='../static')



@portal.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

