from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

from endless_line.data_utils.dashboard_utils import DashboardUtils

ALL_ATTRACTIONS = DashboardUtils().get_attractions()


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
                        html.Div([  # Wrapper div for consistent spacing
                            html.Label(
                                "Select Date",
                                className="fw-bold"
                            ),
                            html.Div(
                                dcc.DatePickerSingle(
                                    id="date-picker-dash",
                                    min_date_allowed=datetime.now().date() + timedelta(days=1),
                                    max_date_allowed=datetime.now().date() + timedelta(days=5),
                                    initial_visible_month=datetime.now().date() + timedelta(days=1),
                                    date=datetime.now().date() + timedelta(days=1),
                                    display_format='DD/MM/YYYY',
                                    placeholder="Select a date",
                                    style={
                                        'width': '100%',
                                    }
                                ),
                                className="mt-2"  # Add top margin
                            )
                        ], className="h-100")
                    ], width=12, md=4, className="mb-3"),

                    # Time Picker Column
                    dbc.Col([
                        html.Div([  # Wrapper div for consistent spacing
                            html.Label(
                                "Select Time",
                                className="fw-bold"
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="selected-hour-dash",
                                    options=[
                                        {"label": f"{i:02d}:00", "value": i}
                                        for i in range(9, 23) # propose future hour only
                                    ],
                                    placeholder="Select time (optional)",
                                    className="mt-2"  # Add top margin
                                ),
                            )
                        ], className="h-100")
                    ], width=12, md=4, className="mb-3"),

                    # Attractions Filter Column
                    dbc.Col([
                        html.Div([  # Wrapper div for consistent spacing
                            html.Label(
                                "Closed Attractions",
                                className="fw-bold"
                            ),
                            html.Div(
                                dcc.Dropdown(
                                    id="closed-attractions-dash",
                                    options=[
                                        {"label": attraction, "value": attraction}
                                        for attraction in ALL_ATTRACTIONS
                                    ],
                                    multi=True,
                                    placeholder="Select closed attractions",
                                    className="mt-2"  # Add top margin
                                ),
                            )
                        ], className="h-100")
                    ], width=12, md=4, className="mb-3"),
                ], className="g-3"),  # Add gap between columns

                # Add toggle switch in a new row
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dbc.Switch(
                                id="graph-type-toggle",
                                label="Scrollable View",
                                value=False,
                                className="mt-2"
                            ),
                        ], className="d-flex align-items-center justify-content-center")
                    ], width=12, className="mb-3"),
                ]),

                # Apply Filters Button row
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
            ], className="p-4")  # Increased padding in card body
        ], className="shadow-sm")
    ], fluid=True, className="mb-4")
