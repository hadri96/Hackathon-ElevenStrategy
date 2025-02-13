from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def create_waiting_forecast(hist_wait, pred_wait, attractions):
    """Create waiting times forecast widget."""
    return dbc.Card([
        dbc.CardBody([
            html.H4("Waiting Times Forecast 🕒", className="mb-3"),
            html.P([
                "The solid lines represent historical waiting times, while the ",
                html.Strong("dotted lines show forecasted values"),
                " for each attraction."
            ], className="text-muted mb-3"),
            dcc.Graph(
                figure=create_waiting_times_plot(hist_wait, pred_wait, attractions),
                config={'displayModeBar': False}
            )
        ])
    ], className="shadow-sm")

def create_waiting_times_plot(hist, pred, attractions):
    """
    Create a waiting time forecast plot showing historical and predicted values for multiple attractions.

    Args:
        hist (DataFrame): Historical waiting times data
        pred (DataFrame): Predicted waiting times data
        attractions (list): List of attractions to display
    """
    # Resample data to reduce points (e.g., every 30 minutes)
    hist = hist.set_index('DEB_TIME').resample('30T').mean().reset_index()
    pred = pred.set_index('DEB_TIME').resample('30T').mean().reset_index()

    # Create figure
    fig = go.Figure()

    # Extended color palette for many attractions
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',  # Default Plotly
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#1a237e', '#ff5722', '#4caf50', '#795548', '#607d8b',  # Material
        '#f06292', '#ba68c8', '#9575cd', '#7986cb', '#64b5f6',
        '#4fc3f7', '#4dd0e1', '#4db6ac', '#81c784', '#aed581',
        '#dce775', '#fff176', '#ffd54f', '#ffb74d', '#ff8a65',  # Extended Material
        '#a1887f', '#90a4ae', '#f48fb1', '#ce93d8', '#b39ddb'   # More colors
    ]

    # Add traces for each attraction
    for idx, attraction in enumerate(attractions):
        color = colors[idx % len(colors)]

        # Historical data
        fig.add_trace(go.Scatter(
            x=hist["DEB_TIME"],
            y=hist[attraction],
            mode="lines",
            line=dict(
                color=color,
                width=2
            ),
            name=attraction,
            hovertemplate=f"{attraction}<br>Wait: %{{y:.0f}} min at %{{x|%H:%M}}<extra></extra>"
        ))

        # Predicted data (dashed)
        fig.add_trace(go.Scatter(
            x=pred["DEB_TIME"],
            y=pred[attraction],
            mode="lines",
            line=dict(
                color=color,
                width=2,
                dash="dash"
            ),
            name=attraction + " (predicted)",
            showlegend=False,
            hovertemplate=f"{attraction} (predicted)<br>Wait: %{{y:.0f}} min at %{{x|%H:%M}}<extra></extra>"
        ))

    # Get unique days for annotations and shapes
    unique_days = sorted(set(hist["DEB_TIME"].dt.date) | set(pred["DEB_TIME"].dt.date))

    # Add vertical lines and day labels
    shapes = []
    annotations = []

    for day in unique_days[1:]:  # Skip first day to avoid line at the start
        # Add vertical line
        shapes.append(dict(
            type='line',
            x0=f"{day} 09:00:00",
            x1=f"{day} 09:00:00",
            y0=0,
            y1=1,
            yref='paper',
            line=dict(
                color='rgba(0,0,0,0.2)',
                width=1,
                dash='dash'
            )
        ))

        # Add day label
        annotations.append(dict(
            x=f"{day} 09:00:00",
            y=1.1,  # Position above the graph
            text=day.strftime('%A'),  # Day name
            showarrow=False,
            xanchor='left',
            yanchor='bottom',
            yref='paper',
            font=dict(size=12)
        ))

    # Update layout
    fig.update_layout(
        title=None,
        margin=dict(t=20, b=40, l=50, r=20),  # Increased bottom margin for labels
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=0,  # Horizontal labels
            title=None,
            dtick=3600 * 24,  # Show tick every day
            ticktext=[f"{day.strftime('%d/%m')}" for day in unique_days],  # Day name and date
            tickvals=[f"{day} 12:00:00" for day in unique_days],  # Center of each day
            rangebreaks=[
                dict(bounds=[22, 9], pattern="hour"),  # Hide hours between 22:00 and 9:00
            ]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            title="Wait Time (minutes)",
            rangemode="tozero"
        ),
        height=400,  # Increased height
        shapes=shapes,
        showlegend=True,
        dragmode=False
    )

    return fig
