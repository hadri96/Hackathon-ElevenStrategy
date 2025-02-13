from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc

def create_waiting_time_kpi(avg_wait_time):
    """
    Create a KPI card showing the average waiting time.

    Args:
        avg_wait_time (float): Average waiting time to display
    """

    return dbc.Card([
        dbc.CardHeader([
            html.H5("Average Wait Time ⏱️", className="mb-0")
        ]),
        dbc.CardBody([
            # Wrapper div for vertical centering
            html.Div([
                # Content container
                html.Div([
                    # Large icon
                    html.I(
                        className="fas fa-clock text-primary mb-3",
                        style={"fontSize": "4rem"}
                    ),
                    # Large number with minutes
                    html.H1([
                        f"{avg_wait_time:.0f}",
                        html.Small(" minutes",
                                 className="text-muted ms-2",
                                 style={"fontSize": "1.8rem"})
                    ], className="mb-3"),

                    # Description
                    html.P(
                        "Average wait time over the last 30 days",
                        className="text-muted mb-0",
                        style={"fontSize": "1.1rem"}
                    )
                ], className="text-center")
            ], className="d-flex align-items-center justify-content-center",
               style={"height": "100%", "minHeight": "350px"})
        ], className="h-100")
    ], className="shadow-sm h-100")

def create_churnrate_kpi(churn_rate):
    """
    Create a KPI card showing the churn rate.

    Args:
        churn_rate (float): Churn rate value to display (as a percentage)
    """
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Potential Churn Rate ⚠️", className="mb-0")
        ]),
        dbc.CardBody([
            # Wrapper div for vertical centering
            html.Div([
                # Content container
                html.Div([
                    # Large icon
                    html.I(
                        className="fas fa-exclamation-triangle text-warning mb-3",
                        style={"fontSize": "4rem"}
                    ),
                    # Large number with percentage
                    html.H1(f"{churn_rate}", className="mb-3"),

                    # Description
                    html.P(
                        "Visitors likely to leave due to wait times",
                        className="text-muted mb-0",
                        style={"fontSize": "1.1rem"}
                    )
                ], className="text-center")
            ], className="d-flex align-items-center justify-content-center",
               style={"height": "100%", "minHeight": "350px"})
        ], className="h-100")
    ], className="shadow-sm h-100")

def create_wtei_ratio(wtei_ratios):
    """
    Create a bar plot showing the WTEI ratios for selected attractions.

    Args:
        wtei_ratios (dict): Dictionary with attraction names as keys and WTEI ratios as values
    """
    # Create the bar plot
    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        x=list(wtei_ratios.keys()),
        y=list(wtei_ratios.values()),
        marker_color='rgb(55, 83, 109)',
        text=[f"{v:.1%}" for v in wtei_ratios.values()],  # Show percentages
        textposition='auto',
    ))

    # Update layout
    fig.update_layout(
        title=None,
        margin=dict(t=20, b=40, l=50, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=300,
        showlegend=False,
        xaxis=dict(
            title=None,
            tickangle=-45,
            showgrid=False,
        ),
        yaxis=dict(
            title="WTEI Ratio",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            tickformat=".0%",  # Format y-axis as percentage
            range=[0, max(wtei_ratios.values()) * 1.1]  # Add 10% padding to top
        ),
    )

    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-chart-bar me-2"),
                html.H5("Wait Time Efficiency Index", className="mb-0"),
            ], className="d-flex align-items-center")
        ]),
        dbc.CardBody([
            dcc.Graph(
                figure=fig,
                config={
                    'displayModeBar': False,
                    'showAxisDragHandles': False,
                    'showAxisRangeEntryBoxes': False,
                    'staticPlot': True
                }
            )
        ])
    ], className="shadow-sm")


