from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from endless_line.data_utils.weather_forecast import WeatherForecast
from datetime import datetime, timedelta

def create_weather_forecast_plot():
    """Create a weather forecast plot with temperature and humidity lines, daily separators, and icons below."""

    # Get weather forecast data
    weather = WeatherForecast()
    forecast_data = weather.get_forecast()

    # Create the figure
    fig = go.Figure()

    # Add temperature line
    fig.add_trace(go.Scatter(
        x=forecast_data['dt_iso'],
        y=forecast_data['temp'],
        mode='lines',
        line=dict(
            color='#FF9933',
            width=3,
            shape='spline'
        ),
        name='Temperature',
        hovertemplate='Temperature: %{y:.1f}°C<br>%{x|%d/%m %H:%M}<extra></extra>'
    ))

    # Add humidity line on secondary axis
    fig.add_trace(go.Scatter(
        x=forecast_data['dt_iso'],
        y=forecast_data['humidity'],
        mode='lines',
        line=dict(
            color='#3366CC',
            width=2,
            shape='spline'
        ),
        name='Humidity',
        yaxis='y2',
        hovertemplate='Humidity: %{y}%<br>%{x|%d/%m %H:%M}<extra></extra>'
    ))

    # Add vertical lines for day separators
    unique_days = forecast_data['dt_iso'].dt.date.unique()
    shapes = []
    for day in unique_days[1:]:  # Skip first day to avoid line at the start
        shapes.append(dict(
            type='line',
            x0=day,
            x1=day,
            y0=0,
            y1=1,
            yref='paper',
            line=dict(
                color='rgba(0,0,0,0.2)',
                width=1,
                dash='dash'
            )
        ))

    # Update layout with secondary axis and day separators
    fig.update_layout(
        title=dict(
            text="Temperature and Humidity Forecast",
            x=0.5,
            xanchor='center'
        ),
        xaxis_title=None,
        yaxis=dict(
            title="Temperature (°C)",
            gridcolor='rgba(255,153,51,0.1)',
            zeroline=False
        ),
        yaxis2=dict(
            title="Humidity (%)",
            anchor="x",
            overlaying="y",
            side="right",
            gridcolor='rgba(51,102,204,0.1)',
            zeroline=False
        ),
        height=300,
        margin=dict(t=50, b=30, l=50, r=50),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=False,  # Removed horizontal grid in favor of day separators
            tickformat='%a\n%d/%m',  # Show day name and date
            dtick='D1',  # Force tick for each day
            tickangle=-45
        ),
        hovermode='x unified',
        shapes=shapes  # Add the day separator lines
    )

    # Get 6-hourly forecast for icons
    icons_data = forecast_data[forecast_data['dt_iso'].dt.hour % 6 == 0].copy()

    # Create simplified weather icons row
    weather_icons = dbc.Row([
        dbc.Col([
            html.Div([
                html.Div(
                    row['dt_iso'].strftime('%H:%M'),
                    className="text-center small"
                ),
                html.Img(
                    src=f"http://openweathermap.org/img/w/{row['weather_icon']}.png",
                    className="mx-auto d-block",
                    style={'width': '40px'}
                )
            ], className="text-center")
        ], width=True)  # Auto-width columns
        for _, row in icons_data.iterrows()
    ], className="g-0 mt-2 align-items-center justify-content-center")

    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-cloud-sun me-2"),
                html.H5("Weather Forecast", className="mb-0"),
            ], className="d-flex align-items-center")
        ]),
        dbc.CardBody([
            # Temperature and humidity graph
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False}
            ),
            # Simple weather icons row
            weather_icons
        ])
    ], className="shadow-sm")
