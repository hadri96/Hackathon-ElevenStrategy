from dash import html, dcc
import dash_bootstrap_components as dbc

def create_feature_card(title, description, icon, link):
    """Create a feature card with clean design"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-2x mb-3"),
                html.H3(title, className="mb-3"),
                html.P(description, className="text-muted"),
                dbc.Button(
                    [
                        "Explore ",
                        html.I(className="fas fa-arrow-right ms-1")
                    ],
                    href=link,
                    color="primary",
                    className="mt-3 hover-grow"
                )
            ], className="text-center")
        ], className="p-4")
    ], className="h-100 shadow-sm card-clean floating")

layout = html.Div([
    # Animated background lights
    html.Div(className="light x1"),
    html.Div(className="light x2"),
    html.Div(className="light x3"),
    html.Div(className="light x4"),
    html.Div(className="light x5"),
    html.Div(className="light x6"),
    html.Div(className="light x7"),

    # Main content
    dbc.Container([
        # Hero Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1(
                        "Welcome to The Endless Line",
                        className="display-4 text-center mb-3 glow-text"
                    ),
                    html.P(
                        "Your AI-powered companion for the perfect theme park experience",
                        className="lead text-center mb-5 fade-in"
                    ),
                ], className="py-5")
            ], width=12)
        ]),

        # Feature Cards
        dbc.Row([
            dbc.Col([
                create_feature_card(
                    "Interactive Dashboard",
                    "Monitor real-time wait times, weather conditions, and crowd levels. Make informed decisions about which attractions to visit next.",
                    "fa-chart-line",
                    "/dashboard"
                )
            ], width=12, md=4, className="mb-4"),

            dbc.Col([
                create_feature_card(
                    "When Should I Go?",
                    "Plan your perfect visit with our AI recommendations. Get personalized suggestions for the best days and times to visit based on historical data.",
                    "fa-calendar-check",
                    "/when-to-go"
                )
            ], width=12, md=4, className="mb-4"),

            dbc.Col([
                create_feature_card(
                    "About Our Project",
                    "Discover how we use machine learning and data analytics to predict wait times and enhance your theme park experience.",
                    "fa-lightbulb",
                    "/about"
                )
            ], width=12, md=4, className="mb-4")
        ], className="g-4"),

        # Footer section
        dbc.Row([
            dbc.Col([
                html.Hr(className="my-5"),
                html.P([
                    "The Endless Line combines real-time data with advanced analytics to help you ",
                    html.Strong("maximize your enjoyment"),
                    " and ",
                    html.Strong("minimize your wait times"),
                    "."
                ], className="text-center text-muted fade-in")
            ], width=12)
        ])
    ], fluid=True, className="py-4 position-relative")
], className="home-container")
