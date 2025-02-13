from dash import html
import dash_bootstrap_components as dbc

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
            # Icon and value in a centered column
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
            ], className="text-center d-flex flex-column justify-content-center",
               style={"minHeight": "250px"})  # Match height with attendance graph
        ])
    ], className="shadow-sm h-100")
