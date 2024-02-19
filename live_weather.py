import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

'''
https://open-meteo.com/en/docs#latitude=54.3781&longitude=18.4682&current=temperature_2m,relative_humidity_2m,rain,snowfall,cloud_cover&hourly=&timezone=Europe%2FBerlin
'''

def get_current_weather():
    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 54.3781,
            "longitude": 18.4682,
            "current": ["temperature_2m", "relative_humidity_2m", "rain", "snowfall", "cloud_cover"],
            "timezone": "Europe/Berlin"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        '''print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")'''

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = round(current.Variables(0).Value(),3)                           # C
        current_relative_humidity_2m = round(current.Variables(1).Value(),3)                     # %
        current_rain = round(current.Variables(2).Value(),3)                                     # mm 
        current_showers = round(current.Variables(3).Value(),3)                                  # mm
        current_snowfall = round(current.Variables(3).Value(),3)                                 # cm
        current_cloud_cover = round(current.Variables(4).Value(),3)                              # %

        return current_temperature_2m, current_relative_humidity_2m, current_rain, current_showers, current_snowfall, current_cloud_cover

    except Exception as e:
        print (f'An error occured while retrieving weather update: {e}')
        return None