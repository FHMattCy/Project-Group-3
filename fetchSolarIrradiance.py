import openmeteo_requests
import requests_cache
import pandas as pd
import os
from retry_requests import retry
from datetime import datetime, timedelta


def fetchSolarIrradiance(latitude, longitude, start_date_time, end_date_time):
    #Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Extract only date parts from datetime strings
    start_date = start_date_time.split('T')[0]
    end_date = end_date_time.split('T')[0]

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "shortwave_radiation",
        # "minutely_15": "shortwave_radiation",
        # "timezone": "Europe/Berlin",
        "start_date": start_date,
        "end_date": end_date
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}N {response.Longitude()}E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_shortwave_radiation = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation

    hourly_dataframe = pd.DataFrame(data = hourly_data)

    # Convert start and end datetime strings to pandas Timestamps with UTC timezone
    start_timestamp = pd.Timestamp(start_date_time).tz_localize('UTC').floor('H')
    end_timestamp = pd.Timestamp(end_date_time).tz_localize('UTC').ceil('H')

    hourly_dataframe = hourly_dataframe[
        (hourly_dataframe['date'] >= start_timestamp) &
        (hourly_dataframe['date'] <= end_timestamp)
    ]

    print(hourly_dataframe)

    #Create a folder name "data"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    #Save as solar_radiation_data.csv to folder name "data"
    # minutely_15_csv_path = os.path.join(data_dir, "minutely_15_solar_radiation_data.csv")
    hourly_csv_path = os.path.join(data_dir, "solar_radiation_data.csv")
    # hourly_csv_path = os.path.join(base_dir, "solar_radiation_data.csv")
    hourly_dataframe.to_csv(hourly_csv_path, index=False)
    print(f"Solar radiation data saved")

    