from flask import Blueprint, render_template

bp = Blueprint('mars', __name__)

@bp.route('/mars')
def index():
    return render_template('mars/index.html') 