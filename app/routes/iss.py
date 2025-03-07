from flask import Blueprint, render_template

bp = Blueprint('iss', __name__)

@bp.route('/iss')
def index():
    return render_template('iss/index.html') 