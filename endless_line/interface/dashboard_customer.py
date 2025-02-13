from dash import html, Input, Output, callback, dcc
import dash_bootstrap_components as dbc
from endless_line.interface.widgets.customer_filter import create_customer_filter
from endless_line.interface.widgets.weather_forecast import create_weather_forecast_plot
from endless_line.interface.widgets.predicted_attendance import create_attendance_forecast
from endless_line.interface.widgets.predicted_waiting import create_waiting_forecast
from endless_line.interface.widgets.kpi import create_waiting_time_kpi
from endless_line.data_utils.dashboard_utils import DashboardUtils
from datetime import datetime, timedelta

# Initialize dashboard utils and compute data
dashboard_utils = DashboardUtils()
ALL_ATTRACTIONS = dashboard_utils.get_attractions()

@callback(
    [Output("waiting-times-container", "children"),
     Output("waiting-time-kpi", "children")],
    Input("attractions-of-interest", "value")
)
def update_dashboard(selected_attractions):
    """Update dashboard elements based on selected attractions."""
    if not selected_attractions:
        selected_attractions = ALL_ATTRACTIONS  # Default to first attraction

    # Compute waiting times data for selected attractions
    current_date = datetime.today()
    hist_wait, pred_wait = dashboard_utils.predicted_waiting_time(
        threshold_date=current_date,
        start_date=current_date - timedelta(days=3),
        attractions=selected_attractions,
    )

    # Create waiting times graph
    waiting_component = create_waiting_forecast(hist_wait, pred_wait, selected_attractions)

    # Update KPI for selected attractions
    avg_wait_time = dashboard_utils.compute_kpi3(attractions=selected_attractions)
    kpi_component = create_waiting_time_kpi(avg_wait_time)

    return waiting_component, kpi_component

layout = dbc.Container([
    # Header Section with Explanation
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("Welcome to Your Park Planner! 🎢",
                       className="display-4 mb-3"),
                html.P([
                    "This dashboard helps you plan your visit to the park by showing wait times and trends for your favorite attractions. ",
                    "You can view daily patterns to plan your visit date to optimize your day at the park. If no attractions are selected, the dashboard will show the average wait time for all attractions."
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
        ], width=12, lg=8, id='attendance-forecast-container'),

        # Average Wait Time KPI
        dbc.Col([
            dcc.Loading(
                id="loading-kpi",
                children=html.Div(id="waiting-time-kpi")
            )
        ], width=12, lg=4)
    ], className="mb-4"),

    # Waiting Times Forecast
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-wait-times",
                children=html.Div(id="waiting-times-container")
            )
        ], width=12)
    ], className="mb-4"),

    # Weather Forecast Row
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-weather",
                children=create_weather_forecast_plot()
            )
        ], width=12)
    ])

], fluid=True, className="py-3")
