import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class NASAAPI:
    BASE_URL = "https://api.nasa.gov"
    API_KEY = os.getenv('NASA_API_KEY')

    @staticmethod
    def _make_request(endpoint, params=None):
        if params is None:
            params = {}
        params['api_key'] = NASAAPI.API_KEY
        
        response = requests.get(f"{NASAAPI.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def get_apod(self, date=None):
        """Get Astronomy Picture of the Day"""
        endpoint = "/planetary/apod"
        params = {'date': date} if date else {}
        return self._make_request(endpoint, params)

    def get_mars_photos(self, rover="perseverance", sol=None, earth_date=None, camera=None, page=1):
        """Get Mars Rover photos with enhanced parameters and error handling"""
        endpoint = f"/mars-photos/api/v1/rovers/{rover}/photos"
        params = {'page': page}

        # Validate and add parameters
        if sol is not None and earth_date is not None:
            raise ValueError("Cannot specify both sol and earth_date")
        
        if sol is not None:
            try:
                params['sol'] = int(sol)
            except ValueError:
                raise ValueError("Sol must be a valid integer")
                
        if earth_date is not None:
            try:
                # Validate date format
                datetime.strptime(earth_date, '%Y-%m-%d')
                params['earth_date'] = earth_date
            except ValueError:
                raise ValueError("earth_date must be in YYYY-MM-DD format")
                
        if camera is not None:
            params['camera'] = camera.upper()

        try:
            return self._make_request(endpoint, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise ValueError("Invalid parameters provided")
            elif e.response.status_code == 404:
                raise ValueError(f"No photos found for rover {rover} with specified parameters")
            else:
                raise

    def get_neo_feed(self, start_date=None, end_date=None):
        """Get Near Earth Objects feed"""
        endpoint = "/neo/rest/v1/feed"
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        return self._make_request(endpoint, params)

    def get_earth_imagery(self, lat, lon, date=None):
        """Get Earth imagery for a specific location"""
        endpoint = "/planetary/earth/imagery"
        params = {
            'lat': lat,
            'lon': lon,
            'date': date if date else datetime.now().strftime("%Y-%m-%d")
        }
        return self._make_request(endpoint, params)

    def get_iss_position(self):
        """Get International Space Station position"""
        endpoint = "/iss/v1/position"
        return self._make_request(endpoint) 