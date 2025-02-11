## TO DO:
## INPUT SECTION
## - Enter a day from the calendar (limited to 5 days in the future)
## - Select potential attractions that are closed
## - Select hour of the day (from 9am to 10pm)
## OUTPUT SECTION
## if no hour is selected:
	## - display weather forecast that day at 12PM
	## for the given date display a plot with:
		## - waiting time for each attraction
		## - bar chart with maximum, minimum and average waiting time through the day for each attraction
## if an hour is selected:
	## - display the weather forecast that day at the selected hour
	## - display the waiting time for each attraction at the selected hour
	## - display the waiting time for each attraction at the selected hour


import dash
import dash_bootstrap_components as dbc
from dash import html
import os
from endless_line.data_utils.dataloader import DataLoader

data_loader = DataLoader()
# Initialize the Dash app with any required external stylesheets
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v6.4.0/css/all.css',
        'https://unpkg.com/aos@2.3.1/dist/aos.css'
    ],
    external_scripts=[
        'https://unpkg.com/aos@2.3.1/dist/aos.js'
    ],
    assets_folder=os.path.join(data_loader.root_dir,'endless_line', 'interface', 'assets')
)

# Create the background div with bubbles
background = html.Div([
    html.Div(className=f"light x{i}") for i in range(1, 16)
], className="background-container")

# Add the background to the app's layout
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div class="background-container">
            ''' + '\n            '.join([f'<div class="light x{i}"></div>' for i in range(1, 61)]) + '''
        </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Configure the app
app.config.suppress_callback_exceptions = True

# Make server available for deployment platforms
server = app.server
