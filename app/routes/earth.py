from flask import Blueprint, render_template, jsonify, request
from app.services.nasa_api import NASAAPI
from datetime import datetime, timedelta
import json

bp = Blueprint('earth', __name__)
nasa_api = NASAAPI()

@bp.route('/earth')
def index():
    # Get events for the map
    try:
        events = nasa_api.get_earth_events()
        categories = nasa_api.get_earth_categories()
    except Exception as e:
        events = {'events': []}
        categories = {'categories': []}
        
    return render_template('earth/index.html',
                         events=events.get('events', []),
                         categories=categories.get('categories', []))

@bp.route('/earth/imagery')
def get_imagery():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    date = request.args.get('date')
    dim = request.args.get('dim', 0.025, type=float)
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
        
    try:
        imagery = nasa_api.get_earth_imagery(lat, lon, date, dim)
        return jsonify(imagery)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/earth/compare')
def get_comparison():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    date1 = request.args.get('date1')
    date2 = request.args.get('date2')
    
    if not all([lat, lon, date1, date2]):
        return jsonify({'error': 'All parameters are required'}), 400
        
    try:
        image1 = nasa_api.get_earth_imagery(lat, lon, date1)
        image2 = nasa_api.get_earth_imagery(lat, lon, date2)
        return jsonify({
            'before': image1,
            'after': image2
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/earth/assets')
def get_assets():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    begin_date = request.args.get('begin_date')
    end_date = request.args.get('end_date')
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
        
    try:
        assets = nasa_api.get_earth_assets(lat, lon, begin_date, end_date)
        return jsonify(assets)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/earth/events')
def get_events():
    category = request.args.get('category')
    days = request.args.get('days', 30, type=int)
    
    try:
        events = nasa_api.get_earth_events()
        if category:
            events['events'] = [e for e in events['events'] if category in [c['id'] for c in e['categories']]]
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            events['events'] = [e for e in events['events'] if datetime.strptime(e['geometry'][0]['date'], '%Y-%m-%dT%H:%M:%SZ') > cutoff]
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 400 