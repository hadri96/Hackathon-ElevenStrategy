from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from endless_line.interface.widgets.filter_operator import create_operator_filter
from endless_line.interface.widgets.predicted_attendance import create_attendance_forecast
from endless_line.interface.widgets.predicted_waiting import create_waiting_forecast
from endless_line.interface.widgets.kpi import create_waiting_time_kpi, create_churnrate_kpi, create_wtei_ratio
from endless_line.data_utils.dashboard_utils import DashboardUtils
from datetime import datetime, timedelta

# Initialize dashboard utils and compute data
dashboard_utils = DashboardUtils()
ALL_ATTRACTIONS = dashboard_utils.get_attractions()

layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("Park Operations Dashboard 🎪",
                       className="display-4 mb-3"),
                html.P([
                    "Monitor park performance, attendance trends, and attraction wait times. ",
                    "Use the filters below to analyze specific time periods and attractions.",
                    "If no attractions are selected, the dashboard will show the wait time for all attractions."
                ], className="lead")
            ], className="py-3")
        ], width=12)
    ]),

    # Filters Section
    dbc.Row([
        dbc.Col([
            create_operator_filter(ALL_ATTRACTIONS)
        ], width=12)
    ]),

    # KPIs Row
    dbc.Row([
        # First KPI
        dbc.Col([
            html.Div(id="operator-kpi-1", children=create_churnrate_kpi(dashboard_utils.compute_kpi1(attractions=ALL_ATTRACTIONS)))
        ], width=12, lg=6, style={"height": "100%"}, id="kpi-row1"),

        # WTEI Widget
        dbc.Col([
            dcc.Loading(
                id="loading-wtei",
                children=html.Div(id="operator-wtei-container")
            )
        ], width=12, lg=6, id="kpi-row2", style={"height": "100%"})
    ], className="mb-4"),

    # Attendance Forecast
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-attendance",
                children=html.Div(id="operator-attendance-container")
            )
        ], width=12)
    ], className="mb-4"),

    # Waiting Times Forecast
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-wait-times",
                children=html.Div(id="operator-waiting-times-container")
            )
        ], width=12)
    ])
], fluid=True, className="py-3")

@callback(
    [Output("operator-attendance-container", "children"),
     Output("operator-waiting-times-container", "children"),
     Output("operator-kpi-1", "children"),
     Output("operator-wtei-container", "children")],
    [Input("apply-operator-filters", "n_clicks")],
    [State("date-range", "start_date"),
     State("date-range", "end_date"),
     State("attractions-of-interest", "value")],
    prevent_initial_call=True
)
def update_operator_dashboard(n_clicks, start_date, end_date, selected_attractions):
    """Update dashboard elements based on selected attractions."""
    if not selected_attractions:
        selected_attractions = ALL_ATTRACTIONS

    # Convert string dates to datetime objects
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.today()
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d') if start_date else end_datetime - timedelta(days=3)

    # Compute waiting times data for selected attractions
    hist_wait, pred_wait = dashboard_utils.predicted_waiting_time(
        threshold_date=end_datetime,
        start_date=start_datetime,
        attractions=selected_attractions,
    )

    # Create waiting times graph
    waiting_component = create_waiting_forecast(hist_wait, pred_wait, selected_attractions)

    # Create attendance forecast
    attendance_component = create_attendance_forecast()


    # Get churn rate for KPI1
    churn_rate = dashboard_utils.compute_kpi1(selected_attractions)
    kpi1 = create_churnrate_kpi(churn_rate)

    # Get WTEI ratios
    wtei_ratios = dashboard_utils.compute_kpi2(selected_attractions)
    kpi2 = create_wtei_ratio(wtei_ratios)

    return attendance_component, waiting_component, kpi1, kpi2
