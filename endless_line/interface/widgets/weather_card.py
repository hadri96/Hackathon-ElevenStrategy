import datetime

from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

def create_weather_card(weather_info):
    """
    Expects a dictionary (or Pandas row with `.get()`) with keys like:
      - dt_txt
      - temp
      - feels_like
      - weather_main
      - weather_description
      - weather_icon
      - humidity
      - wind_speed

    Returns a dbc.Card object with relevant weather info.
    """
    icon_code = weather_info.get("weather_icon", "01d")  # default if missing
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"

    date_str = weather_info.get("dt_iso", "N/A")  # "2025-02-10 18:00:00"
    dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    formatted_dt = dt_obj.strftime("%b %d, %I:%M %p")
    main_condition = weather_info.get("weather_main", "Clear")
    description = weather_info.get("weather_description", "").capitalize()
    temp = weather_info.get("temp", 0)
    feels_like = weather_info.get("feels_like", 0)
    humidity = weather_info.get("humidity", 0)
    wind_speed = weather_info.get("wind_speed", 0)
    time_text = f"at {dt_obj.hour:02d}:00"
    # Create a short date/time label, e.g. "2025-02-10 18:00"
    # (You might want to reformat it more nicely.)

    # Build the card layout
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-cloud me-2"),
                html.H5(f"Weather Forecast on {formatted_dt}", className="card-title"),
            ], className="d-flex align-items-center")
        ]),
        dbc.CardBody([
            # Existing weather card content from lines 43-60
            html.H4(f"{main_condition}", className="card-title"),
            html.P(description, className="card-text"),
            html.Img(src=icon_url, alt="Weather Icon", style={"height": "60px"}),
            html.P(
                f"Temperature: {temp:.1f}°C (feels like {feels_like:.1f}°C)",
                className="card-text"
            ),
            html.P(f"Humidity: {humidity}%", className="card-text"),
            html.P(f"Wind speed: {wind_speed:.1f} m/s", className="card-text"),
        ])
    ], className="shadow-sm w-100")
