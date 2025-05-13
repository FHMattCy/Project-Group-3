import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# format of start_date and end_date is "YYYY-MM-DD"
def fetchHistoricalData(latitude, longitude, start_date, end_date):

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Weather API URL and parameters
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "rain", "snowfall", "cloud_cover", "relative_humidity_2m", "wind_speed_10m", "apparent_temperature", "shortwave_radiation"]
    }
    
    responses = openmeteo.weather_api(url, params=params)
    
    # Process first location response
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
    
    # Process hourly data
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(2).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(6).ValuesAsNumpy()
    hourly_shortwave_radiation = hourly.Variables(7).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m,
        "rain": hourly_rain,
        "snowfall": hourly_snowfall,
        "cloud_cover": hourly_cloud_cover,
        "relative_humidity_2m": hourly_relative_humidity_2m,
        "wind_speed_10m": hourly_wind_speed_10m,
        "apparent_temperature": hourly_apparent_temperature,
        "shortwave_radiation" : hourly_shortwave_radiation

    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print(hourly_dataframe)

    # Save the historical data to a CSV file
    # hourly_dataframe.to_csv("historical_weather_data.csv", index=False)
    # print("Data saved to 'historical_weather_data.csv'.")
    
    return hourly_dataframe  # Return the DataFrame with the data

