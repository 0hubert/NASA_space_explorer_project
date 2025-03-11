from flask import Blueprint, render_template, jsonify, request
from app.services.nasa_api import NASAAPI
from datetime import datetime, timedelta
import json
from app.models import ClimateData, db
import math
import random

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

def generate_sample_climate_data(lat, lon):
    """Generate realistic sample climate data based on latitude and rough climate patterns"""
    today = datetime.now()
    start_date = today - timedelta(days=365)
    
    # Base temperature varies by latitude (rough approximation)
    base_temp = 30 - abs(lat) * 0.5  # Higher temps near equator, lower near poles
    
    # Base precipitation (rough approximation)
    base_precip = 100 - abs(lat)  # More rain near equator
    if base_precip < 20:
        base_precip = 20  # Minimum baseline precipitation
    
    data = []
    current_date = start_date
    
    while current_date <= today:
        # Temperature variation by season (reversed for southern hemisphere)
        season_factor = math.cos((current_date.timetuple().tm_yday / 365) * 2 * math.pi)
        if lat < 0:  # Southern hemisphere
            season_factor = -season_factor
            
        # Add some random variation
        temp_variation = random.uniform(-3, 3)
        precip_variation = random.uniform(0, base_precip * 0.5)
        
        # Calculate temperature and precipitation
        temperature = base_temp + (season_factor * 10) + temp_variation
        precipitation = max(0, (base_precip + precip_variation) * (1 + season_factor * 0.2))
        
        # Create climate data entry
        climate_data = ClimateData(
            latitude=lat,
            longitude=lon,
            date=current_date.date(),
            temperature=round(temperature, 1),
            precipitation=round(precipitation, 1)
        )
        data.append(climate_data)
        
        current_date += timedelta(days=1)
    
    return data

@bp.route('/earth/climate')
def get_climate_data():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    
    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
        
    try:
        # Query last 12 months of climate data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        climate_data = ClimateData.query.filter(
            ClimateData.latitude.between(lat - 0.5, lat + 0.5),
            ClimateData.longitude.between(lon - 0.5, lon + 0.5),
            ClimateData.date.between(start_date, end_date)
        ).order_by(ClimateData.date).all()
        
        # If no data exists, generate sample data
        if not climate_data:
            climate_data = generate_sample_climate_data(lat, lon)
            # Save to database
            db.session.bulk_save_objects(climate_data)
            db.session.commit()
        
        dates = []
        temperatures = []
        precipitation = []
        
        for data in climate_data:
            dates.append(data.date.strftime('%Y-%m-%d'))
            temperatures.append(data.temperature)
            precipitation.append(data.precipitation)
            
        return jsonify({
            'dates': dates,
            'temperatures': temperatures,
            'precipitation': precipitation
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400 