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

def create_attendance_kpi(attendance_value):
    """
    Create a KPI card showing the attendance value.

    Args:
        attendance_value (int): Attendance value to display
    """
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Daily Attendance 👥", className="mb-0")
        ]),
        dbc.CardBody([
            # Wrapper div for vertical centering
            html.Div([
                # Content container
                html.Div([
                    # Large icon
                    html.I(
                        className="fas fa-users text-primary mb-3",
                        style={"fontSize": "4rem"}
                    ),
                    # Large number with visitors
                    html.H1([
                        f"{attendance_value}",
                        html.Small(" visitors",
                                 className="text-muted ms-2",
                                 style={"fontSize": "1.8rem"})
                    ], className="mb-3"),

                    # Description
                    html.P(
                        "Expected attendance for today",
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
