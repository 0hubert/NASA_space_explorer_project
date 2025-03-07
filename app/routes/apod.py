from flask import Blueprint, render_template

bp = Blueprint('apod', __name__)

@bp.route('/apod')
def index():
    return render_template('apod/index.html') 