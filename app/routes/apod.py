from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.services.nasa_api import NASAAPI
from app.models import APOD, Favorite, db
from datetime import datetime

bp = Blueprint('apod', __name__)
nasa_api = NASAAPI()

@bp.route('/apod')
def index():
    # Get the date parameter from URL, default to today
    date_str = request.args.get('date')
    try:
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.now().date()
    except ValueError:
        flash('Invalid date format', 'danger')
        return redirect(url_for('apod.index'))

    # Try to get from database first
    apod_entry = APOD.query.filter_by(date=date).first()
    
    if not apod_entry:
        try:
            # Fetch from NASA API
            apod_data = nasa_api.get_apod(date=date_str)
            
            # Save to database
            apod_entry = APOD(
                date=date,
                title=apod_data['title'],
                explanation=apod_data['explanation'],
                image_url=apod_data['url'],
                media_type=apod_data['media_type']
            )
            db.session.add(apod_entry)
            db.session.commit()
        except Exception as e:
            flash('Error fetching APOD data', 'danger')
            return render_template('apod/index.html', error=str(e))

    # Check if this APOD is in user's favorites
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            nasa_id=str(apod_entry.date)
        ).first() is not None

    return render_template('apod/index.html', 
                         apod=apod_entry,
                         is_favorite=is_favorite,
                         current_date=date)

@bp.route('/apod/favorite', methods=['POST'])
@login_required
def toggle_favorite():
    date = request.form.get('date')
    apod = APOD.query.filter_by(date=datetime.strptime(date, '%Y-%m-%d').date()).first()
    
    if not apod:
        return jsonify({'error': 'APOD not found'}), 404
        
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        nasa_id=str(apod.date)
    ).first()
    
    if existing_favorite:
        db.session.delete(existing_favorite)
        is_favorite = False
    else:
        new_favorite = Favorite(
            user_id=current_user.id,
            title=apod.title,
            nasa_id=str(apod.date),
            image_url=apod.image_url
        )
        db.session.add(new_favorite)
        is_favorite = True
    
    db.session.commit()
    return jsonify({'is_favorite': is_favorite}) 