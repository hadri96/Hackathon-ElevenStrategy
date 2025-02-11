from dash import html
import dash_bootstrap_components as dbc

def create_feature_card(title, description, icon, link):
    """Create a feature card with consistent styling"""
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
                    className="mt-3"
                )
            ], className="text-center")
        ], className="p-4")
    ], className="h-100 shadow-sm hover-shadow")

layout = dbc.Container([
    # Hero Section
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to The Endless Line", className="display-4 text-center mb-3"),
            html.P(
                "Your AI-powered companion for the perfect theme park experience",
                className="lead text-center text-muted mb-5"
            ),
        ], width=12)
    ], className="py-5"),

    # Feature Cards
    dbc.Row([
        # Dashboard Card
        dbc.Col([
            create_feature_card(
                "Interactive Dashboard",
                "Check our dashboard to see how the next days might look like at the park! We show our predictions for real-time wait times, weather conditions, and crowd levels. Make informed decisions about which attractions to visit next.",
                "fa-chart-line",
                "/dashboard"
            )
        ], width=12, md=4, className="mb-4"),

        # When Should I Go Card
        dbc.Col([
            create_feature_card(
                "When Should I Go?",
                "Plan your perfect visit with our AI recommendations. Get personalized suggestions for the best days and times to visit based on your preferences.",
                "fa-calendar-check",
                "/when-to-go"
            )
        ], width=12, md=4, className="mb-4"),

        # About Card
        dbc.Col([
            create_feature_card(
                "About Our Project",
                "Discover how we use machine learning and data analytics to predict wait times and enhance your theme park experience.",
                "fa-lightbulb",
                "/about"
            )
        ], width=12, md=4, className="mb-4")
    ], className="g-4"),

    # Additional Info Section
    dbc.Row([
        dbc.Col([
            html.Hr(className="my-5"),
            html.P([
                "The Endless Line combines real-time data with advanced analytics to help you ",
                html.Strong("maximize your enjoyment"),
                " and ",
                html.Strong("minimize your wait times"),
                "."
            ], className="text-center text-muted")
        ], width=12)
    ])
], fluid=True, className="py-4")

# CSS remains the same
"""
.hover-shadow {
    transition: all 0.3s ease;
}

.hover-shadow:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}
"""
