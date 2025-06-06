import openmeteo_requests
import requests_cache
import pandas as pd
import os
from retry_requests import retry


def fetchSolarIrradiance(latitude, longitude):
    #Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    #Make sure all required weather variables are listed here
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "shortwave_radiation",
        "timezone": "Europe/Berlin",
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)

    #Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}N {response.Longitude()}E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    #Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }

#Make the radiation look more clearly and able to appear inn terminal
    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print(hourly_dataframe)

#Create a folder name "Data"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "Data")
    os.makedirs(data_dir, exist_ok=True)

    #Save as solar_radiation_data.csv to folder name "Data"
    csv_path = os.path.join(data_dir, "solar_radiation_data.csv")
    hourly_dataframe.to_csv(csv_path, index=False)
    print(f"Solar radiation data saved to {csv_path}")

    