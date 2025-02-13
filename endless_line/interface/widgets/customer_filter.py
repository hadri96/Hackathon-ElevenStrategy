from dash import html, dcc
import dash_bootstrap_components as dbc

def create_customer_filter(ALL_ATTRACTIONS):
    """Create a horizontal filter widget for customer dashboard."""

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Attractions Multi-Select
                dbc.Col([
                    html.Label(
                        "Select Attractions 🎢",
                        className="fw-bold"
                    ),
                    dcc.Dropdown(
                        id='attractions-of-interest',
                        options=[{'label': attr, 'value': attr} for attr in ALL_ATTRACTIONS],
                        value=None,
                        multi=True,
                        className="mt-1"
                    )
                ], width=12, lg=6, id='attractions-of-interest-dropdown'),


                # Apply Button
                dbc.Col([
                    html.Label("\u00A0", className="fw-bold d-block"),  # Invisible label for alignment
                    dbc.Button(
                        "Apply Filters",
                        id="apply-customer-filters",
                        color="primary",
                        className="w-100 mt-1"
                    )
                ], width=12, lg=2)
            ], className="g-2 align-items-end")
        ])
    ], className="shadow-sm mb-4")
