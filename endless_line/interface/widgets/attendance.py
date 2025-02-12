from dash import html
import dash_bootstrap_components as dbc

def create_attendance_widget(attendance_value=None):
    """
    Create an attendance widget showing current park attendance

    Args:
        attendance_value (int, optional): Current attendance number
    """
    if attendance_value is None:
        attendance_value = 0

    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className="fas fa-users me-2"),
                html.H5("Park Attendance", className="card-title"),
            ], className="d-flex align-items-center")
        	]),
        dbc.CardBody([
            # Attendance number with separator
            html.H3(
                f"{attendance_value:}",
                className="mb-0 text-primary"
            ),
        ], className="p-3")
    ], className="mb-3 w-100 shadow-sm")
