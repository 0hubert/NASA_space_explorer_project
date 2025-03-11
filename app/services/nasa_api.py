import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
from functools import wraps
import math

load_dotenv()

def rate_limit(calls_per_second=2):
    """Rate limiting decorator"""
    min_interval = 1.0 / float(calls_per_second)
    def decorator(func):
        last_time_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_time_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            ret = func(*args, **kwargs)
            last_time_called[0] = time.time()
            return ret
        return wrapper
    return decorator

class NASAAPI:
    BASE_URL = "https://api.nasa.gov"
    ISS_BASE_URL = "http://api.open-notify.org"
    API_KEY = os.getenv('NASA_API_KEY')

    def __init__(self):
        if not self.API_KEY:
            raise ValueError("NASA API key not found. Please set NASA_API_KEY in your environment variables.")
        
    @staticmethod
    @rate_limit(calls_per_second=2)
    def _make_request(endpoint, params=None):
        if params is None:
            params = {}
        params['api_key'] = NASAAPI.API_KEY
        
        try:
            response = requests.get(
                f"{NASAAPI.BASE_URL}{endpoint}",
                params=params,
                timeout=10  # 10 seconds timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise TimeoutError("Request to NASA API timed out. Please try again later.")
        except requests.RequestException as e:
            raise ConnectionError(f"Error connecting to NASA API: {str(e)}")

    @staticmethod
    def _make_iss_request(endpoint, params=None):
        """Make request to Open Notify API for ISS data"""
        if params is None:
            params = {}
        try:
            response = requests.get(
                f"{NASAAPI.ISS_BASE_URL}{endpoint}",
                params=params,
                timeout=5  # 5 seconds timeout for ISS API
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise TimeoutError("Request to ISS API timed out. Please try again later.")
        except requests.RequestException as e:
            raise ConnectionError(f"Error connecting to ISS API: {str(e)}")

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

    def get_earth_assets(self, lat, lon, begin_date=None, end_date=None):
        """Get available Earth imagery dates for a location using GIBS Worldview"""
        today = datetime.now().date()
        
        try:
            if begin_date:
                begin = datetime.strptime(begin_date, '%Y-%m-%d').date()
                if begin > today:
                    raise ValueError("Cannot request imagery for future dates")
            else:
                begin = today - timedelta(days=365)
                
            if end_date:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                if end > today:
                    raise ValueError("Cannot request imagery for future dates")
            else:
                end = today
                
            if begin > end:
                raise ValueError("Begin date must be before end date")

            # Calculate a wider bounding box (roughly 12-degree area)
            bbox = f"{lon-6},{lat-6},{lon+6},{lat+6}"
            date_str = begin.strftime('%Y-%m-%d')

            # Generate Worldview URL
            url = (
                f"https://wvs.earthdata.nasa.gov/api/v1/snapshot?"
                f"REQUEST=GetSnapshot&"
                f"TIME={date_str}&"
                f"BBOX={bbox}&"
                f"CRS=EPSG:4326&"
                f"LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&"
                f"WIDTH=1600&"  # Increased width for better detail
                f"HEIGHT=1600&"  # Increased height for better detail
                f"FORMAT=image/jpeg"
            )

            return {
                'results': [{
                    'date': date_str,
                    'url': url
                }]
            }
        except ValueError as e:
            raise ValueError(str(e))

    def get_earth_imagery(self, lat, lon, date=None, dim=0.025):
        """Get Earth imagery for a specific location using GIBS Worldview"""
        today = datetime.now().date()
        
        try:
            if date:
                request_date = datetime.strptime(date, '%Y-%m-%d').date()
                if request_date > today:
                    raise ValueError("Cannot request imagery for future dates")
            else:
                request_date = today - timedelta(days=30)

            # Calculate a wider bounding box (roughly 12-degree area)
            bbox = f"{lon-6},{lat-6},{lon+6},{lat+6}"
            date_str = request_date.strftime('%Y-%m-%d')

            # Generate Worldview URL with adjusted parameters
            url = (
                f"https://wvs.earthdata.nasa.gov/api/v1/snapshot?"
                f"REQUEST=GetSnapshot&"
                f"TIME={date_str}&"
                f"BBOX={bbox}&"
                f"CRS=EPSG:4326&"
                f"LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&"
                f"WIDTH=1600&"  # Increased width for better detail
                f"HEIGHT=1600&"  # Increased height for better detail
                f"FORMAT=image/jpeg"
            )

            return {
                'date': date_str,
                'url': url
            }
        except Exception as e:
            raise ValueError(f"Error generating Earth imagery URL: {str(e)}")

    def get_earth_events(self):
        """Get EONET (Earth Observatory Natural Event Tracker) events"""
        endpoint = "/EONET/v3/events"
        return self._make_request(endpoint)

    def get_earth_categories(self):
        """Get EONET event categories"""
        endpoint = "/EONET/v3/categories"
        return self._make_request(endpoint)

    def get_earth_layers(self):
        """Get available Earth imagery layers"""
        endpoint = "/planetary/earth/layers"
        return self._make_request(endpoint)

    def get_iss_position(self):
        """Get current ISS position"""
        return self._make_iss_request("/iss-now.json")

    def get_iss_pass_times(self, lat, lon):
        """Get ISS pass predictions for a location"""
        params = {
            'lat': lat,
            'lon': lon,
            'alt': 0,  # altitude in meters above sea level
            'n': 10  # Number of passes to predict
        }
        try:
            return self._make_iss_request("/iss-pass.json", params)
        except requests.exceptions.RequestException as e:
            # If the primary endpoint fails, use the backup calculation
            return self._calculate_pass_predictions(lat, lon)

    def _calculate_pass_predictions(self, lat, lon):
        """Calculate ISS pass predictions when the API is unavailable"""
        current_time = datetime.now()
        predictions = []
        
        try:
            # Get current ISS position
            iss_data = self.get_iss_position()
            iss_lat = float(iss_data['iss_position']['latitude'])
            iss_lon = float(iss_data['iss_position']['longitude'])
            
            # ISS orbital parameters
            orbital_period = 92.68  # minutes
            orbital_height = 408    # km
            earth_radius = 6371     # km
            visibility_radius = 2000 # km
            
            # Calculate next 10 passes
            for i in range(10):
                # Calculate future position based on orbital mechanics
                pass_time = current_time + timedelta(minutes=orbital_period * (i + 1))
                
                # Calculate ground track progression
                time_diff = (pass_time - current_time).total_seconds() / 60  # in minutes
                lon_progression = (time_diff / orbital_period) * 360  # degrees
                new_lon = (iss_lon + lon_progression) % 360
                
                # Calculate if visible from location
                lat_diff = abs(lat - iss_lat)
                lon_diff = min(abs(new_lon - lon), 360 - abs(new_lon - lon))
                
                # Use great circle distance formula
                distance = earth_radius * 2 * abs(
                    math.asin(
                        math.sqrt(
                            math.sin(math.radians(lat_diff) / 2) ** 2 +
                            math.cos(math.radians(lat)) *
                            math.cos(math.radians(iss_lat)) *
                            math.sin(math.radians(lon_diff) / 2) ** 2
                        )
                    )
                )
                
                if distance <= visibility_radius:
                    # Calculate visibility duration based on orbital velocity
                    duration = int(
                        (2 * math.acos(earth_radius / (earth_radius + orbital_height)) *
                        (earth_radius + orbital_height) / 7.66) # 7.66 km/s is ISS velocity
                    )
                    
                    predictions.append({
                        'risetime': int(pass_time.timestamp()),
                        'duration': duration,
                        'max_elevation': int(90 - math.degrees(math.asin(distance / visibility_radius)))
                    })
            
            return {
                'message': 'Calculated predictions (approximations)',
                'response': predictions
            }
        except Exception as e:
            print(f"Error calculating ISS predictions: {e}")
            return {
                'message': 'Error in prediction calculations',
                'response': []
            }

    def get_astronauts(self):
        """Get current astronauts in space"""
        return self._make_iss_request("/astros.json") 