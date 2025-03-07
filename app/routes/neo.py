from flask import Blueprint, render_template

bp = Blueprint('neo', __name__)

@bp.route('/neo')
def index():
    return render_template('neo/index.html') 