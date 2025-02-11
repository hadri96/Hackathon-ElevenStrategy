import dash_bootstrap_components as dbc
from dash import html

def create_navbar():
    """
    Create the main navigation bar with improved styling and structure.

    Returns:
        dbc.Navbar: Bootstrap navigation component with custom styling
    """
    # Define navigation links
    nav_links = [
        dbc.NavItem(
            dbc.NavLink(
                "Home",
                href="/",
                className="nav-link-custom"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "About",
                href="/about",
                className="nav-link-custom"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Dashboard",
                href="/dashboard",
                className="nav-link-custom"
            )
        ),
    ]

    # Create the navbar
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Logo/Brand section
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.I(className="fas fa-chart-line me-2")),  # Font Awesome icon
                            dbc.Col(dbc.NavbarBrand("Endless Line Dashboard", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),

                # Toggle button for mobile
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

                # Collapsible content
                dbc.Collapse(
                    dbc.Nav(
                        nav_links,
                        className="ms-auto",
                        navbar=True
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="light",
        dark=False,
        className="navbar-custom shadow-sm",
    )

    return navbar
