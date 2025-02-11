from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

ALL_ATTRACTIONS = [
    "Roller Coaster",
    "Ferris Wheel",
    "Haunted House",
    "Merry-Go-Round",
    "Bumper Cars"
]

def create_filter_menu():
    """Create a clean, contained filter section for the dashboard."""
    return dbc.Container([
        dbc.Card([
            dbc.CardHeader([
                html.H4("Filter Options", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    # Date Picker Column
                    dbc.Col([
                        html.Label("Select Date", className="fw-bold mb-2"),
                        dcc.DatePickerSingle(
                            id="date-picker-dash",
                            min_date_allowed=datetime.now().date(),
                            max_date_allowed=datetime.now().date() + timedelta(days=5),
                            initial_visible_month=datetime.now().date(),
                            date=datetime.now().date(),
                            className="w-100"
                        ),
                    ], width=12, md=4, className="mb-3"),

                    # Time Picker Column
                    dbc.Col([
                        html.Label("Select Time", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id="selected-hour-dash",
                            options=[
                                {"label": f"{i:02d}:00", "value": i}
                                for i in range(9, 23)  # 9 AM to 10 PM
                            ],
                            placeholder="Select time (optional)",
                            className="w-100"
                        ),
                    ], width=12, md=4, className="mb-3"),

                    # Attractions Filter Column
                    dbc.Col([
                        html.Label("Closed Attractions", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id="closed-attractions-dash",
                            options=[
                                {"label": attraction, "value": attraction}
                                for attraction in ALL_ATTRACTIONS
                            ],
                            multi=True,
                            value=[],
                            placeholder="Select closed attractions",
                            className="w-100"
                        ),
                    ], width=12, md=4, className="mb-3"),
                ]),

                # Apply Filters Button
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Apply Filters",
                            id="apply-filters-button",
                            color="primary",
                            className="w-100"
                        ),
                    ], width=12, md={"size": 4, "offset": 4}, className="mt-3")
                ])
            ])
        ], className="shadow-sm")
    ], fluid=True, className="mb-4")
