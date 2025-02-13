from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_operator_filter(ALL_ATTRACTIONS):
    """Create a horizontal filter widget for operator dashboard."""

    # Calculate date ranges
    today = datetime.today().date()
    min_date = today - timedelta(days=30)
    max_date = today + timedelta(days=5)

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Date Range Picker
                dbc.Col([
                    html.Label(
                        "Select Date Range 📅",
                        className="fw-bold"
                    ),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=today - timedelta(days=3),
                        end_date=today + timedelta(days=2),
                        className="mt-1",
                        display_format="DD/MM/YYYY"
                    )
                ], width=12, lg=4),

                # Attractions Multi-Select
                dbc.Col([
                    html.Label(
                        "Select Attractions 🎢",
                        className="fw-bold"
                    ),
                    dcc.Dropdown(
                        id='attractions-of-interest',
                        options=[{'label': attr, 'value': attr} for attr in ALL_ATTRACTIONS],
                        value=[ALL_ATTRACTIONS[0]],
                        multi=True,
                        className="mt-1"
                    )
                ], width=12, lg=6),

                # Apply Button
                dbc.Col([
                    html.Label("\u00A0", className="fw-bold d-block"),  # Invisible label for alignment
                    dbc.Button(
                        "Apply Filters",
                        id="apply-operator-filters",
                        color="primary",
                        className="w-100 mt-1"
                    )
                ], width=12, lg=2)
            ], className="g-2 align-items-end")
        ])
    ], className="shadow-sm mb-4")
