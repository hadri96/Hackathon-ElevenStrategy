from dash import html
import dash_bootstrap_components as dbc
from endless_line.interface.widgets.customer_filter import create_customer_filter
from endless_line.interface.widgets.weather_forecast import create_weather_forecast_plot
from endless_line.interface.widgets.predicted_attendance import create_attendance_forecast
from endless_line.data_utils.dashboard_utils import DashboardUtils

dashboard_utils = DashboardUtils()
ALL_ATTRACTIONS = dashboard_utils.get_attractions()


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
                ], className="lead")
            ], className="py-3")
        ], width=12)
    ]),

    # Filters Section
    dbc.Row([
        dbc.Col([
            create_customer_filter(ALL_ATTRACTIONS)
        ], width=12)
    ]),

    # Main Visualizations
    dbc.Row([
        # Attendance Forecast
        dbc.Col([
            create_attendance_forecast()
        ], width=12, lg=8),

        # Daily Statistics
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Daily Statistics 📊", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="daily-stats")
                ])
            ], className="shadow-sm h-100")
        ], width=12, lg=4)
    ], className="mb-4"),

    # Secondary Visualizations
    dbc.Row([
        # Crowd Patterns
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Attraction Wait Times 🎡", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="customer-graph")
                ])
            ], className="shadow-sm h-100")
        ], width=12, lg=6),

        # Peak Hours
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Peak Hours Analysis ⏰", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="customer-stats")
                ])
            ], className="shadow-sm h-100")
        ], width=12, lg=6)
    ], className="mb-4"),

    # Weather Forecast Row
    dbc.Row([
        dbc.Col([
            create_weather_forecast_plot()
        ], width=12)
    ])

], fluid=True, className="py-3")
