from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.services.nasa_api import NASAAPI
from app.models import MarsPhoto, db
from datetime import datetime, timedelta
from functools import lru_cache
import json

bp = Blueprint('mars', __name__)
nasa_api = NASAAPI()

# Cache for mission timeline data
MISSION_TIMELINE = [
    {
        'title': 'Perseverance Launch',
        'date': 'July 30, 2020',
        'description': 'Perseverance launched from Cape Canaveral Air Force Station, Florida.'
    },
    {
        'title': 'Perseverance Landing',
        'date': 'February 18, 2021',
        'description': 'Successfully landed in Jezero Crater, Mars.'
    },
    {
        'title': 'Curiosity Launch',
        'date': 'November 26, 2011',
        'description': 'Curiosity launched from Cape Canaveral Air Force Station, Florida.'
    },
    {
        'title': 'Curiosity Landing',
        'date': 'August 6, 2012',
        'description': 'Successfully landed in Gale Crater, Mars.'
    },
    {
        'title': 'Opportunity Launch',
        'date': 'July 7, 2003',
        'description': 'Opportunity launched from Cape Canaveral Air Force Station, Florida.'
    },
    {
        'title': 'Opportunity Landing',
        'date': 'January 25, 2004',
        'description': 'Successfully landed in Meridiani Planum, Mars.'
    },
    {
        'title': 'Spirit Launch',
        'date': 'June 10, 2003',
        'description': 'Spirit launched from Cape Canaveral Air Force Station, Florida.'
    },
    {
        'title': 'Spirit Landing',
        'date': 'January 4, 2004',
        'description': 'Successfully landed in Gusev Crater, Mars.'
    }
]

@lru_cache(maxsize=100)
def get_cached_photos(rover, camera, earth_date, sol):
    """Cache Mars photos to improve performance"""
    cache_key = f"{rover}:{camera}:{earth_date}:{sol}"
    
    try:
        # Try to get from database first
        if earth_date:
            photos = MarsPhoto.query.filter_by(
                rover_name=rover,
                earth_date=datetime.strptime(earth_date, '%Y-%m-%d').date()
            )
            if camera:
                photos = photos.filter_by(camera_name=camera)
            photos = photos.all()
            
            if photos:
                return photos

        # If not in database, fetch from API
        params = {}
        if earth_date:
            params['earth_date'] = earth_date
        if sol:
            params['sol'] = sol
        if camera:
            params['camera'] = camera

        photos_data = nasa_api.get_mars_photos(rover=rover, **params)
        
        # Store in database for future use
        if photos_data and 'photos' in photos_data:
            for photo_data in photos_data['photos']:
                try:
                    photo = MarsPhoto(
                        nasa_id=str(photo_data['id']),
                        rover_name=rover,
                        camera_name=photo_data['camera']['name'],
                        image_url=photo_data['img_src'],
                        earth_date=datetime.strptime(photo_data['earth_date'], '%Y-%m-%d').date()
                    )
                    db.session.add(photo)
                except (KeyError, ValueError) as e:
                    print(f"Error processing photo data: {e}")
                    continue
            
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error committing to database: {e}")
                db.session.rollback()
        
        return photos_data.get('photos', [])
    except Exception as e:
        print(f"Error in get_cached_photos: {e}")
        return []

@bp.route('/mars')
def index():
    # Get filter parameters
    rover = request.args.get('rover', 'perseverance')
    camera = request.args.get('camera', '')
    earth_date = request.args.get('earth_date', '')
    sol = request.args.get('sol', '')

    # Get photos using cached function
    photos = get_cached_photos(rover, camera, earth_date, sol)

    # Get available cameras for the selected rover
    rover_cameras = {
        'perseverance': ['NAVCAM_LEFT', 'NAVCAM_RIGHT', 'MASTCAM_Z_LEFT', 'MASTCAM_Z_RIGHT', 
                        'FRONT_HAZCAM_LEFT_A', 'FRONT_HAZCAM_RIGHT_A', 'REAR_HAZCAM_LEFT', 'REAR_HAZCAM_RIGHT'],
        'curiosity': ['FHAZ', 'RHAZ', 'MAST', 'CHEMCAM', 'MAHLI', 'MARDI', 'NAVCAM'],
        'opportunity': ['FHAZ', 'RHAZ', 'NAVCAM', 'PANCAM', 'MINITES'],
        'spirit': ['FHAZ', 'RHAZ', 'NAVCAM', 'PANCAM', 'MINITES']
    }

    return render_template('mars/index.html',
                         photos=photos,
                         rover=rover,
                         camera=camera,
                         earth_date=earth_date,
                         sol=sol,
                         cameras=rover_cameras.get(rover, []),
                         mission_timeline=MISSION_TIMELINE) 