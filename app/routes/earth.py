from flask import Blueprint, render_template

bp = Blueprint('earth', __name__)

@bp.route('/earth')
def index():
    return render_template('earth/index.html') 