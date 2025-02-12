from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from endless_line.interface import home, about, dashboard, when
from endless_line.interface.widgets.navbar import create_navbar
from endless_line.interface.app import app, server
  # import page layouts

# Define the main menu or navigation bar (optional)
navbar = create_navbar()

# This is the main app layout, with a Location component and a container
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    html.Div(id="page-content", className="p-4")
])

# Callback to handle page routing
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/about":
        return about.layout
    elif pathname == "/dashboard":
        return dashboard.layout
    elif pathname in ["/when-to-go", "/when"]:
        return when.layout
    else:
        # Handle 404 - Page Not Found
        raise Exception(f"404 - Page not found: {pathname}")
        return html.H1("404: Page not found", className="text-danger")

@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    """Toggle the navbar collapse on mobile devices."""
    if n:
        return not is_open
    return is_open
if __name__ == "__main__":
    # Run the server
    app.run_server(debug=True)

