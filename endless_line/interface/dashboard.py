import datetime
import random

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from endless_line.interface.widgets.weather_card import create_weather_card
from endless_line.interface.widgets.filter_menu import create_filter_menu
from endless_line.interface.widgets.attendance import create_attendance_widget
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from endless_line.data_utils.weather_forecast import WeatherForecast
import json
from endless_line.data_utils.dashboard_utils import DashboardUtils
from attendance_prediction_model.attendance_pred import attendance_forecasting
from warnings import filterwarnings

filterwarnings("ignore")


# Import your app instance from app.py
from endless_line.interface.app import app

########################################
# Mock Data & Utility Functions
########################################

board_utils = DashboardUtils()

ALL_ATTRACTIONS = board_utils.get_attractions()


def get_mock_wait_times(selected_date):
    hours = list(range(9, 23))  # 9 AM to 10 PM
    data = []
    for hour in hours:
        for attraction in ALL_ATTRACTIONS:
            wait_time = random.randint(5, 120)
            data.append({
                "hour": hour,
                "attraction": attraction,
                "wait_time": wait_time
            })
    return pd.DataFrame(data)

########################################
# Layout
########################################

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("The Endless Line Dashboard"), width=12)
    ], className="my-3"),

    create_filter_menu(),

    # ---- OUTPUT SECTION ----
    dbc.Row([
        # Weather Forecast and Attendance Column
        dbc.Col([
            html.Div(id="attendance-widget-dash", className="mb-3"),  # Added margin-bottom
            html.Div(id="weather-forecast-dash")
        ], width=4, className="d-flex flex-column"),  # Added flex display

        # Graphs with header card
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.I(className="fas fa-chart-line me-2"),
                        html.H5("Predictive Analytics", className="card-title"),
                    ], className="d-flex align-items-center")
                ]),
                dbc.CardBody([
                    # Wrap the main graph in a div with dynamic height
                    html.Div(
                        dcc.Graph(
                            id="main-graph-dash",
                            config={'displayModeBar': False}
                        ),
                        id="graph-container",
                        style={
                            'border': '1px solid #ddd',
                            'border-radius': '4px',
                            'margin': '10px 5px'
                        }
                    ),
                    dcc.Graph(id="stats-bar-graph-dash",
                              style={
                            'border': '1px solid #ddd',
                            'border-radius': '4px',
                            'padding': '0 20px',
                            'margin': '10px'
                        }),
                ], className="p-3")
            ], className="shadow-sm")
        ], width=8)
    ])
], fluid=True)


########################################
# Callbacks
########################################
@app.callback(
    [
        Output("attendance-widget-dash", "children"),
        Output("weather-forecast-dash", "children"),
        Output("main-graph-dash", "figure"),
        Output("stats-bar-graph-dash", "figure")
    ],
    [
        Input("apply-filters-button", "n_clicks")
    ],
    [
        State("date-picker-dash", "date"),
        State("selected-hour-dash", "value"),
        State("closed-attractions-dash", "value"),
        State("graph-type-toggle", "value")
    ]
)
def update_dashboard(n_clicks, selected_date, selected_hour, closed_attractions, is_scrollable):
    # Get wait times data
    date_obj = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
    df_wait = get_mock_wait_times(date_obj)

    # Filter out closed attractions if any
    if closed_attractions:
        df_wait = df_wait[~df_wait["attraction"].isin(closed_attractions)]

    if selected_hour is None:
        selected_hour = datetime.datetime.now().hour+1  # Default to actual hour +1
        if is_scrollable:
            # Create a subplot for each attraction
            open_attractions = [attr for attr in ALL_ATTRACTIONS if attr not in (closed_attractions or [])]
            n_attractions = len(open_attractions)

            fig_main = make_subplots(
                rows=n_attractions,
                cols=1,
                subplot_titles=open_attractions,
                vertical_spacing=0.08  # Increased spacing between subplots
            )

            for idx, attraction in enumerate(open_attractions, 1):
                attraction_data = df_wait[df_wait["attraction"] == attraction]

                fig_main.add_trace(
                    go.Scatter(
                        x=attraction_data["hour"],
                        y=attraction_data["wait_time"],
                        name=attraction,
                        mode='lines+markers',
                        showlegend=False
                    ),
                    row=idx,
                    col=1
                )

                fig_main.update_yaxes(
                    title_text="Wait Time (min)",
                    row=idx,
                    col=1,
                    range=[0, df_wait["wait_time"].max() * 1.1]
                )

            fig_main.update_layout(
                title=f"Individual Attraction Wait Times ({selected_date})",
                height=300 * n_attractions,  # Increased height per subplot
                showlegend=False,
                margin=dict(
                    t=70,   # Top margin for title
                    b=50,   # Bottom margin
                    l=50,   # Left margin
                    r=20,   # Right margin
                    pad=10  # Padding between plots
                ),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            # Set common x-axis title only for the bottom plot
            fig_main.update_xaxes(
                title_text="Hour of Day",
                row=n_attractions,
                col=1,
                rangeslider=dict(visible=True)
            )

        else:
            # Standard view
            fig_main = px.line(
                df_wait, x="hour", y="wait_time", color="attraction",
                title=f"Hourly Waiting Times ({selected_date})",
                markers=True
            )
            fig_main.update_layout(
                xaxis_title="Hour of Day",
                yaxis_title="Wait Time (min)",
                height=450,  # Fixed height for standard view
                margin=dict(
                    t=70,
                    b=50,
                    l=50,
                    r=20
                ),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

        # Create stats figure for daily view
        stats_df = df_wait.groupby('attraction').agg({
            'wait_time': ['min', 'max', 'mean']
        }).reset_index()
        stats_df.columns = ['attraction', 'min_wait', 'max_wait', 'avg_wait']

        fig_stats = px.bar(
            stats_df,
            x='attraction',
            y=['min_wait', 'max_wait', 'avg_wait'],
            title=f"Wait Time Statistics ({selected_date})",
            barmode='group',
            labels={
                'value': 'Wait Time (min)',
                'variable': 'Statistic',
                'attraction': 'Attraction'
            }
        )

    else:
        # Hourly view
        hour_data = df_wait[df_wait["hour"] == selected_hour]

        fig_main = px.bar(
            hour_data,
            x="attraction",
            y="wait_time",
            title=f"Wait Times at {selected_hour:02d}:00 ({selected_date})"
        )

        fig_stats = px.scatter(
            hour_data,
            x="attraction",
            y="wait_time",
            title=f"Wait Time Distribution at {selected_hour:02d}:00"
        )

    # Create attendance widget and weather card
    attendance = 25000  # Replace with actual attendance data
    out = attendance_forecasting()
    attendance = DashboardUtils().get_attendance(out, selected_date)

    attendance_widget = create_attendance_widget(attendance)

    weather_forecast = WeatherForecast().get_forecast(selected_date, selected_hour)
    if not weather_forecast.empty:
        weather_forecast['dt_iso'] = weather_forecast['dt_iso'].dt.strftime('%Y-%m-%d %H:%M:%S')
        row = json.dumps(weather_forecast.iloc[0].to_dict())
        row = json.loads(row)
    else:
        raise ValueError(f"No weather forecast data available at: {selected_date} {selected_hour}")
    weather_str = create_weather_card(row)  # Assuming row is defined somewhere

    return attendance_widget, weather_str, fig_main, fig_stats

# Add a new callback to control container style
@app.callback(
    Output("graph-container", "style"),
    [
        Input("selected-hour-dash", "value"),
        Input("graph-type-toggle", "value")
    ]
)
def update_container_style(selected_hour, is_scrollable):
    base_style = {
        'border': '1px solid #ddd',
        'border-radius': '4px'
    }

    # If we're showing multiple graphs (no hour selected and scrollable view)
    if selected_hour is None and is_scrollable:
        base_style.update({
            'height': '750px',  # Height to show ~3 graphs
            'overflow-y': 'auto'  # Enable vertical scrolling
        })

    return base_style
