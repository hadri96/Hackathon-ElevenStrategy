from dash import html, dcc
import dash_bootstrap_components as dbc
from endless_line.interface.widgets.customer_filter import create_customer_filter
from endless_line.data_utils.dashboard_utils import DashboardUtils
from endless_line.interface.app import app

layout = dbc.Container([
    # Header Section with Explanation
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("Welcome to Your Park Planner! 🎢",
                       className="display-4 mb-3"),
                html.P([
                    "This dashboard helps you plan your visit to the park by showing wait times and trends for your favorite attractions. ",
                    "You can view either daily patterns to plan your visit date, or hourly details to optimize your day at the park."
                ], className="lead"),
                html.Hr(className="my-4"),
                html.P([
                    html.Strong("How to use this dashboard:"),
                    html.Ul([
                        html.Li("Select your attractions of interest from the dropdown menu"),
                        html.Li("Choose between daily overview or hourly details"),
                        html.Li("Click 'Apply Filters' to update the view"),
                    ], className="mt-2")
                ], className="text-muted")
            ], className="py-4")
        ], width=12)
    ], className="mb-4"),

    # Main Content
    dbc.Row([
        # Left Column - Filters
        dbc.Col([
            create_customer_filter()
        ], width=12, lg=3, className="mb-4"),

        # Right Column - Visualizations
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="customer-graph", className="mb-4"),
                    html.Div(id="customer-stats")
                ])
            ], className="shadow-sm")
        ], width=12, lg=9)
    ])
], fluid=True, className="py-4")
