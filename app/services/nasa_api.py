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

    def get_mars_photos(self, rover="perseverance", sol=None, earth_date=None):
        """Get Mars Rover photos"""
        endpoint = f"/mars-photos/api/v1/rovers/{rover}/photos"
        params = {}
        if sol:
            params['sol'] = sol
        if earth_date:
            params['earth_date'] = earth_date
        return self._make_request(endpoint, params)

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