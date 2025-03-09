from flask import Blueprint, render_template, jsonify, request
from app.services.nasa_api import NASAAPI
from app.models import NEO, db
from datetime import datetime, timedelta
import json

bp = Blueprint('neo', __name__)
nasa_api = NASAAPI()

def validate_date_range(start_date, end_date):
    """Validate the date range for NEO API requests"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        warnings = []
        
        # Add warnings for potentially problematic date ranges
        if (end - start).days > 7:
            warnings.append(f"Selected range is {(end - start).days} days. The NASA API works best with 7-day ranges.")
        
        if start.date() < datetime.now().date() - timedelta(days=365*2):
            warnings.append("Historical data beyond 2 years may have limited availability.")
            
        if end.date() > datetime.now().date() + timedelta(days=365):
            warnings.append("Future predictions beyond 1 year may be less accurate.")
            
        return True, warnings if warnings else None
    except ValueError:
        return False, ["Invalid date format. Use YYYY-MM-DD"]

@bp.route('/neo')
def index():
    # Get default dates
    default_start = datetime.now().strftime('%Y-%m-%d')
    default_end = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    start_date = request.args.get('start_date', default_start)
    end_date = request.args.get('end_date', default_end)
    
    # Validate date range
    is_valid, warnings = validate_date_range(start_date, end_date)
    if not is_valid:
        return render_template('neo/index.html', 
                             error=warnings[0],
                             start_date=default_start,
                             end_date=default_end)
    
    try:
        neo_data = nasa_api.get_neo_feed(start_date=start_date, end_date=end_date)
        processed_data = process_neo_data(neo_data)
        
        return render_template('neo/index.html',
                            neo_data=processed_data,
                            start_date=start_date,
                            end_date=end_date,
                            warnings=warnings)
    except Exception as e:
        return render_template('neo/index.html', 
                             error=f"Error fetching NEO data: {str(e)}",
                             start_date=default_start,
                             end_date=default_end)

@bp.route('/neo/data')
def get_neo_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Validate date range
    is_valid, warnings = validate_date_range(start_date, end_date)
    if not is_valid:
        return jsonify({'error': warnings[0]}), 400
    
    try:
        neo_data = nasa_api.get_neo_feed(start_date=start_date, end_date=end_date)
        response_data = process_neo_data(neo_data)
        if warnings:
            response_data['warnings'] = warnings
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': f"Error fetching NEO data: {str(e)}"}), 400

def process_neo_data(neo_data):
    processed_data = {
        'daily_counts': {},
        'hazardous_counts': {'hazardous': 0, 'non_hazardous': 0},
        'size_distribution': {'small': 0, 'medium': 0, 'large': 0},
        'closest_approaches': [],
        'all_objects': []
    }
    
    for date, asteroids in neo_data['near_earth_objects'].items():
        processed_data['daily_counts'][date] = len(asteroids)
        
        for asteroid in asteroids:
            # Process hazard assessment
            if asteroid['is_potentially_hazardous_asteroid']:
                processed_data['hazardous_counts']['hazardous'] += 1
            else:
                processed_data['hazardous_counts']['non_hazardous'] += 1
            
            # Process size distribution
            diameter_km = (asteroid['estimated_diameter']['kilometers']['estimated_diameter_min'] +
                         asteroid['estimated_diameter']['kilometers']['estimated_diameter_max']) / 2
            
            if diameter_km < 0.5:
                processed_data['size_distribution']['small'] += 1
            elif diameter_km < 2:
                processed_data['size_distribution']['medium'] += 1
            else:
                processed_data['size_distribution']['large'] += 1
            
            # Process closest approaches
            close_approach = min(asteroid['close_approach_data'],
                               key=lambda x: float(x['miss_distance']['kilometers']))
            
            processed_data['closest_approaches'].append({
                'name': asteroid['name'],
                'distance_km': float(close_approach['miss_distance']['kilometers']),
                'velocity_kph': float(close_approach['relative_velocity']['kilometers_per_hour']),
                'approach_date': close_approach['close_approach_date']
            })
            
            # Store complete object data
            processed_data['all_objects'].append({
                'id': asteroid['neo_reference_id'],
                'name': asteroid['name'],
                'diameter_km': diameter_km,
                'hazardous': asteroid['is_potentially_hazardous_asteroid'],
                'velocity_kph': float(close_approach['relative_velocity']['kilometers_per_hour']),
                'miss_distance_km': float(close_approach['miss_distance']['kilometers']),
                'approach_date': close_approach['close_approach_date']
            })
    
    # Sort closest approaches
    processed_data['closest_approaches'] = sorted(
        processed_data['closest_approaches'],
        key=lambda x: x['distance_km']
    )[:5]  # Keep only top 5 closest 