from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

ALL_ATTRACTIONS = [
    "Magic Kingdom",
    "EPCOT",
    "Disney's Hollywood Studios",
    "Disney's Animal Kingdom",
    "Disney Springs"
]

def create_date_options():
    """Create date options for the next 5 days"""
    today = datetime.now()
    date_options = []
    for i in range(5):
        date = today + timedelta(days=i)
        date_options.append({
            'label': date.strftime("%A, %B %d"),  # e.g., "Monday, June 5"
            'value': date.strftime("%Y-%m-%d")
        })
    return date_options

def create_when_to_go_filters(attractions_list):
    """
    Create a comprehensive filter menu for the When Should I Go page

    Args:
        attractions_list (list): List of available attractions
    """
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Customize Your Visit", className="mb-0")
        ]),
        dbc.CardBody([
            # Must-Do Attractions
            dbc.Row([
                dbc.Col([
                    html.Label("Must-Do Attractions", className="fw-bold"),
                    html.Small(
                        "Select the attractions you don't want to miss🙌",
                        className="text-muted d-block mb-2"
                    ),
                    dcc.Dropdown(
                        id="must-do-attractions",
                        options=[
                            {"label": attraction, "value": attraction}
                            for attraction in attractions_list
                        ],
                        multi=True,
                        placeholder="Select attractions..."
                    )
                ], width=12, className="mb-4")
            ]),

            # Possible Dates
            dbc.Row([
                dbc.Col([
                    html.Label("Possible Visit Dates📅", className="fw-bold"),
                    html.Small(
                        "Select one or more dates in the next 5 days",
                        className="text-muted d-block mb-2"
                    ),
                    dcc.Dropdown(
                        id="visit-dates",
                        options=create_date_options(),
                        multi=True,
                        placeholder="Select dates..."
                    )
                ], width=12, className="mb-4")
            ]),

            # Weather Resistance
            dbc.Row([
                dbc.Col([
                    html.Label("Weather Resistance 🌈", className="fw-bold"),
                    html.Small(
                        "How brave are you when it comes to weather?",
                        className="text-muted d-block mb-2"
                    ),
                    dcc.Slider(
                        id="weather-resistance",
                        min=0,
                        max=10,
                        step=2,
                        value=6,
                        marks={
                            0: "Rain-shy ☔",
                            3: "Adaptable 🌦",
                            6: "Tough 💪",
                            8: "Fearless ⚡",
                            10: "Unstoppable 🌪"
                        }
                    )
                ], width=12, className="mb-4")
            ]),

            # Time Slot Preference
            dbc.Row([
                dbc.Col([
                    html.Label("Preferred Time Slot🕰️", className="fw-bold"),
                    html.Small(
                        "When would you like to visit the park?",
                        className="text-muted d-block mb-2"
                    ),
                    dcc.RangeSlider(
                        id="time-slot",
                        min=9,
                        max=22,
                        step=1,
                        value=[9, 16],
                        marks={
                            9: "9:00",
                            12: "12:00",
                            15: "15:00",
                            18: "18:00",
                            22: "22:00"
                        }
                    )
                ], width=12, className="mb-4")
            ]),

            # Visit Duration
            dbc.Row([
                dbc.Col([
                    html.Label("Ideal Visit Duration⏳", className="fw-bold"),
                    html.Small(
                        "How long would you like to spend in the park?",
                        className="text-muted d-block mb-2"
                    ),
                    dcc.Slider(
                        id="visit-duration",
                        min=2,
                        max=13,
                        step=1,
                        value=6,
                        marks={
                            2: "2h",
                            6: "6h",
                            9: "9h",
                            13: "13h"
                        }
                    )
                ], width=12, className="mb-4")
            ]),

            # Apply Button
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-magic me-2"),
                            "Find Best Times"
                        ],
                        id="find-times-button",
                        color="primary",
                        className="w-100"
                    )
                ], width={"size": 6, "offset": 3})
            ])
        ], className="p-4")
    ], className="shadow-sm")
