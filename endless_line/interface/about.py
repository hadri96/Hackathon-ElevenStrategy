from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("About Endless Line 🎢", className="display-4 text-center mb-4"),
                html.Hr(className="my-4")
            ])
        ], width=12)
    ], className="mb-4"),

    # Project Context Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2([
                        html.I(className="fas fa-lightbulb me-2 text-primary"),
                        "Project Context"
                    ], className="mb-3"),
                    html.P(
                        "Endless Line is a data-driven initiative aimed at optimizing waiting times at PortAventura. "
                        "Following the post-COVID-19 period, the park has experienced a significant increase in waiting times, "
                        "negatively impacting visitor satisfaction. Our goal is to analyze waiting times in relation to attendance, "
                        "identify inefficiencies, and provide actionable insights to improve queue management.",
                        className="lead text-muted"
                    )
                ])
            ], className="shadow-sm mb-4")
        ], width=12)
    ]),

    # Objectives & KSF Section
    dbc.Row([
        # Objectives Column
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2([
                        html.I(className="fas fa-bullseye me-2 text-primary"),
                        "Objectives"
                    ], className="mb-3"),
                    html.P(
                        "We aim to improve key performance indicators (KPIs) within the next year. "
                        "This will be achieved by leveraging advanced forecasting models, integrating real-time data, "
                        "and offering an intuitive analytical dashboard for decision-makers.",
                        className="text-muted"
                    )
                ])
            ], className="shadow-sm h-100")
        ], width=12, lg=6, className="mb-4"),

        # Key Success Factors Column
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2([
                        html.I(className="fas fa-star me-2 text-primary"),
                        "Key Success Factors"
                    ], className="mb-3"),
                    html.Ul([
                        html.Li([html.I(className="fas fa-check text-success me-2"), "Business-Oriented: We design solutions tailored to operational needs"]),
                        html.Li([html.I(className="fas fa-robot text-success me-2"), "AI Expertise: Our team applies cutting-edge machine learning techniques"]),
                        html.Li([html.I(className="fas fa-users text-success me-2"), "Customer-Driven: We prioritize enhancing the visitor experience"]),
                        html.Li([html.I(className="fas fa-headset text-success me-2"), "Dedicated Support: We offer ongoing maintenance and support"])
                    ], className="text-muted")
                ])
            ], className="shadow-sm h-100")
        ], width=12, lg=6, className="mb-4")
    ]),

    # Team Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2([
                        html.I(className="fas fa-people-group me-2 text-primary"),
                        "Meet the Team"
                    ], className="mb-3"),
                    html.P(
                        "Our multidisciplinary team combines technical expertise with business acumen to bridge the gap between data science and operational strategy.",
                        className="text-muted mb-4"
                    ),
                    dbc.Row([
                        dbc.Col([
                            html.Ul([
                                html.Li([html.I(className="fas fa-user-tie me-2 text-primary"), "Armand Chambaud - Consultant in Business Analytics"]),
                                html.Li([html.I(className="fas fa-code me-2 text-primary"), "Hadrien Morand - Software Engineer"]),
                                html.Li([html.I(className="fas fa-database me-2 text-primary"), "Henri Mayoud - Data Analyst"])
                            ], className="text-muted")
                        ], width=12, md=6),
                        dbc.Col([
                            html.Ul([
                                html.Li([html.I(className="fas fa-brain me-2 text-primary"), "Jonathan Piscart - Data Scientist"]),
                                html.Li([html.I(className="fas fa-chart-line me-2 text-primary"), "Kirandeep Gaur - Risk Analyst"]),
                                html.Li([html.I(className="fas fa-magnifying-glass-chart me-2 text-primary"), "Théo Van Eccelpoel - Data Analyst"])
                            ], className="text-muted")
                        ], width=12, md=6)
                    ])
                ])
            ], className="shadow-sm mb-4")
        ], width=12)
    ]),

    # What's Next Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2([
                        html.I(className="fas fa-rocket me-2 text-primary"),
                        "What's Next?"
                    ], className="mb-3"),
                    html.P(
                        "Our roadmap includes refining our prediction models, integrating real-time ticketing data, "
                        "and continuously improving our dashboard to provide valuable insights for park operations.",
                        className="text-muted mb-0"
                    )
                ])
            ], className="shadow-sm")
        ], width=12)
    ])
], fluid=True, className="py-4")
