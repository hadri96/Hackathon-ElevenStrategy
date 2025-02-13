from dash import html, dcc
import dash_bootstrap_components as dbc
from endless_line.data_utils.dashboard_utils import DashboardUtils

def create_customer_filter():
    """Create a filter widget for customer dashboard."""

    # Get list of attractions
    ALL_ATTRACTIONS = DashboardUtils().get_attractions()

    return dbc.Card([
        dbc.CardHeader([
            html.H4("Customize Your View", className="mb-0 d-flex align-items-center"),
        ]),
        dbc.CardBody([
            # Attractions Multi-Select
            dbc.Row([
                dbc.Col([
                    html.Label(
                        "Select Attractions of Interest 🎢",
                        className="fw-bold"
                    ),
                    html.Small(
                        "Choose one or more attractions to monitor",
                        className="text-muted d-block mb-2"
                    ),
                    dcc.Dropdown(
                        id='attractions-of-interest',
                        options=[{'label': attr, 'value': attr} for attr in ALL_ATTRACTIONS],
                        value=[ALL_ATTRACTIONS[0]],  # Default to first attraction
                        multi=True,
                        className="mb-3"
                    )
                ], width=12)
            ]),

            # View Type Toggle
            dbc.Row([
                dbc.Col([
                    html.Label(
                        "View Type 📊",
                        className="fw-bold"
                    ),
                    html.Small(
                        "Choose between daily overview or hourly details",
                        className="text-muted d-block mb-2"
                    ),
                    dbc.RadioItems(
                        id='view-type-toggle',
                        options=[
                            {'label': ' Daily Overview', 'value': 'daily'},
                            {'label': ' Hourly Details', 'value': 'hourly'}
                        ],
                        value='daily',
                        inline=True,
                        className="mb-3"
                    )
                ], width=12)
            ]),

            # Apply Button
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Apply Filters",
                        id="apply-customer-filters",
                        color="primary",
                        className="w-100 mt-2"
                    )
                ], width=12)
            ])
        ])
    ], className="shadow-sm")
