from dash import html
import dash_bootstrap_components as dbc
from endless_line.interface.widgets.when_to_go_filters import create_when_to_go_filters

# List of attractions (you can move this to a central configuration later)
ALL_ATTRACTIONS = [
    "Roller Coaster",
    "Ferris Wheel",
    "Haunted House",
    "Merry-Go-Round",
    "Bumper Cars"
]

layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col([
            html.H2("When Should I Go?", className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-magic me-2 text-primary fa-2x float-start"),
                        html.Div([
                            html.H5("Your Personal Theme Park Advisor", className="mb-2"),
                            html.P([
                                "Ready to maximize the fun and minimize the wait? ",
                                "Our AI-powered system will analyze real-time data, weather forecasts, and historical patterns ",
                                "to find your perfect park visit time. Just tell us your preferences, and we'll do the magic! ✨"
                            ], className="text-muted mb-0")
                        ])
                    ], className="d-flex align-items-start")
                ], className="p-4")
            ], className="shadow-sm mb-4")
        ], width=12)
    ], className="mt-4"),

    # Main Content
    dbc.Row([
        # Filters Column
        dbc.Col([
            create_when_to_go_filters(ALL_ATTRACTIONS)
        ], width=12, md=4),

        # Results Column (placeholder for now)
        dbc.Col([
            html.Div(id="recommendations-container")
        ], width=12, md=8)
    ], className="g-4")

], fluid=True, className="py-3")
