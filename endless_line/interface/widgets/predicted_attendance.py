from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
from endless_line.data_utils.dashboard_utils import DashboardUtils

def create_attendance_forecast(start_date: datetime.date = datetime.today() - timedelta(days=5)):
    """Create an attendance forecast plot showing historical and predicted values."""

    dashboard_utils = DashboardUtils()

    # Get date ranges
    current_date = datetime.today()
    # Get historical and predicted data
    hist, pred = dashboard_utils.get_predicted_attendance_with_past(current_date, start_date)

    # Create figure
    fig = go.Figure()

    # Add historical data
    fig.add_trace(go.Scatter(
        x=hist["USAGE_DATE"],
        y=hist["attendance"],
        mode="lines",
        line=dict(
            color="#2E86C1",  # Darker blue
            width=3
        ),
        line_shape="spline",
        name="Historical",
        hovertemplate="Date: %{x|%d/%m}<br>Attendance: %{y:,.0f}<extra></extra>"
    ))

    # Add transition line
    transition_x = [hist["USAGE_DATE"].iloc[-1], pred["USAGE_DATE"].iloc[0]]
    transition_y = [hist["attendance"].iloc[-1], pred["attendance"].iloc[0]]

    fig.add_trace(go.Scatter(
        x=transition_x,
        y=transition_y,
        mode="lines",
        line=dict(
            color="#2E86C1",
            width=2,
            dash="dot"
        ),
        line_shape="spline",
        showlegend=False,
        hovertemplate="Date: %{x|%d/%m}<br>Attendance: %{y:,.0f}<extra></extra>"
    ))

    # Add predicted data
    fig.add_trace(go.Scatter(
        x=pred["USAGE_DATE"],
        y=pred["attendance"],
        mode="lines",
        line=dict(
            color="#E74C3C",  # Red
            width=3
        ),
        line_shape="spline",
        name="Predicted",
        hovertemplate="Date: %{x|%d/%m}<br>Attendance: %{y:,.0f}<extra></extra>"
    ))

    # Update layout
    fig.update_layout(
        title=None,  # We'll use card header instead
        margin=dict(t=20, b=20, l=50, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            tickformat="%d/%m",
            tickangle=-45,
            title=None
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            title="Visitors",
            rangemode="tozero"
        ),
        height=300
    )
    del hist, pred
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-users me-2"),
                html.H5("Park Attendance Forecast", className="mb-0"),
            ], className="d-flex align-items-center")
        ]),
        dbc.CardBody([
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            )
        ])
    ], className="shadow-sm")
