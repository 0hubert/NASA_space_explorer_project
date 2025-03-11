from flask import Blueprint, render_template, jsonify, request
from app.services.nasa_api import NASAAPI
from datetime import datetime
import json

bp = Blueprint('iss', __name__)
nasa_api = NASAAPI()

@bp.route('/iss')
def index():
    try:
        # Get current astronauts in space
        astronauts = nasa_api.get_astronauts()
        
        # Get current ISS position
        iss_position = nasa_api.get_iss_position()
        
        return render_template('iss/index.html',
                             astronauts=astronauts['people'],
                             iss_position=iss_position['iss_position'],
                             timestamp=datetime.fromtimestamp(iss_position['timestamp']))
    except Exception as e:
        return render_template('iss/index.html', error=str(e))

@bp.route('/iss/position')
def get_position():
    """API endpoint for getting current ISS position"""
    try:
        position = nasa_api.get_iss_position()
        return jsonify(position)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/iss/pass-predictions')
def get_pass_predictions():
    """API endpoint for getting ISS pass predictions"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if lat is None or lon is None:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
            
        print(f"Fetching pass predictions for lat: {lat}, lon: {lon}")  # Debug print
        predictions = nasa_api.get_iss_pass_times(lat, lon)
        print(f"Received predictions: {predictions}")  # Debug print
        
        if 'response' not in predictions:
            return jsonify({'error': 'Invalid response format from ISS API'}), 500
            
        return jsonify(predictions)
    except Exception as e:
        print(f"Error in pass predictions: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 400

@bp.route('/iss/crew')
def get_crew():
    """API endpoint for getting current ISS crew information"""
    try:
        astronauts = nasa_api.get_astronauts()
        return jsonify(astronauts)
    except Exception as e:
        return jsonify({'error': str(e)}), 400 