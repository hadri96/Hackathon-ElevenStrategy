import datetime
import random

import dash
from dash import dcc, html, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from endless_line.interface.widgets.weather_card import create_weather_card
from endless_line.interface.widgets.filter_menu import create_filter_menu
import plotly.express as px
import pandas as pd


# Import your app instance from app.py
from endless_line.interface.app import app

########################################
# Mock Data & Utility Functions
########################################

ALL_ATTRACTIONS = [
    "Roller Coaster",
    "Ferris Wheel",
    "Haunted House",
    "Merry-Go-Round",
    "Bumper Cars"
]


def get_mock_wait_times(selected_date):
    hours = list(range(9, 23))  # 9 AM to 10 PM
    data = []
    for hour in hours:
        for attraction in ALL_ATTRACTIONS:
            wait_time = random.randint(5, 120)
            data.append({
                "hour": hour,
                "attraction": attraction,
                "wait_time": wait_time
            })
    return pd.DataFrame(data)

########################################
# Layout
########################################

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.H2("Theme Park Wait Times Dashboard"), width=12)
            ],
            className="my-3"
        ),

        create_filter_menu(),

        # ---- OUTPUT SECTION ----
        dbc.Row([
            # Weather Forecast
            dbc.Col([
                html.H5("Weather Forecast", className="mt-3"),
                # IMPORTANT: We keep a placeholder Div for the weather card(s).
                # The callback will populate this with a dbc.Card (or multiple cards) instead of just text.
                html.Div(id="weather-forecast-dash")
            ], width=4),

            # Graphs
            dbc.Col([
                dcc.Graph(id="main-graph-dash"),
                dcc.Graph(id="stats-bar-graph-dash"),
            ], width=8)
        ])
    ],
    fluid=True
)


########################################
# Callbacks
########################################
@app.callback(
    [
        Output("weather-forecast-dash", "children"),
        Output("main-graph-dash", "figure"),
        Output("stats-bar-graph-dash", "figure")
    ],
    [
        Input("apply-filters-button", "n_clicks")
    ],
    [
        State("date-picker-dash", "date"),
        State("selected-hour-dash", "value"),
        State("closed-attractions-dash", "value")
    ]
)

def update_dashboard(n_clicks, selected_date, selected_hour, closed_attractions):
    if not n_clicks:  # Initial load
        return no_update, no_update, no_update
    """
    - If selected_hour is None:
        - Show 12PM forecast
        - Show line chart (hour vs. wait_time) across 9-22 for each attraction
        - Show bar chart of min, max, average wait time per attraction
    - If selected_hour is set:
        - Show forecast at that hour
        - Show bar chart of wait_time for each attraction at that hour
        - Show second chart (e.g., scatter) for the same data
    """
    if not selected_date:
        return "", dash.no_update, dash.no_update
    row = {
        "dt_txt": "2025-02-10 18:00:00",
        "temp": 5.59,
        "feels_like": 3.96,
        "weather_main": "Rain",
        "weather_description": "moderate rain",
        "weather_icon": "10n",
        "humidity": 97.0,
        "wind_speed": 2.1
        # ... any other fields
    }

    # 2) Turn that dict into a "sexy" card

    weather_str = create_weather_card(row)
    date_obj = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
    df_wait = get_mock_wait_times(date_obj)

    # Filter out closed attractions
    if closed_attractions:
        df_wait = df_wait[~df_wait["attraction"].isin(closed_attractions)]

    if selected_hour is None:
        # 1) Weather at 12 PM
        # 2) Line chart for the day
        fig_main = px.line(
            df_wait, x="hour", y="wait_time", color="attraction",
            title=f"Hourly Waiting Times ({date_obj})", markers=True
        )
        fig_main.update_layout(xaxis_title="Hour of Day", yaxis_title="Wait Time (min)")

        # 3) Bar chart (min, max, avg)
        summary = df_wait.groupby("attraction")["wait_time"].agg(["min", "max", "mean"]).reset_index()
        summary = summary.rename(columns={"min": "Min", "max": "Max", "mean": "Average"})

        melted = summary.melt(id_vars="attraction", var_name="Metric", value_name="Value")
        fig_stats = px.bar(
            melted, x="attraction", y="Value", color="Metric",
            barmode="group",
            title="Min / Max / Average Wait Times"
        )
        fig_stats.update_layout(xaxis_title="Attraction", yaxis_title="Wait Time (min)")

    else:
        # Hour is selected
        df_hour = df_wait[df_wait["hour"] == selected_hour].copy()

        if df_hour.empty:
            fig_main = px.bar(title="All attractions are closed at this hour.")
            fig_stats = px.bar(title="No data to display.")
        else:
            fig_main = px.bar(
                df_hour, x="attraction", y="wait_time",
                title=f"Waiting Time at {selected_hour}:00 ({date_obj})",
                color="attraction"
            )
            fig_main.update_layout(xaxis_title="Attraction", yaxis_title="Wait Time (min)")

            # Second chart (could be anything—here a scatter):
            fig_stats = px.scatter(
                df_hour, x="attraction", y="wait_time",
                size="wait_time", color="attraction",
                title="(Alternate) Wait Time Display"
            )
            fig_stats.update_layout(xaxis_title="Attraction", yaxis_title="Wait Time (min)")

    return weather_str, fig_main, fig_stats
