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
            <div class="light x1"></div>
            <div class="light x2"></div>
            <div class="light x3"></div>
            <div class="light x4"></div>
            <div class="light x5"></div>
            <div class="light x6"></div>
            <div class="light x7"></div>
            <div class="light x8"></div>
            <div class="light x9"></div>
            <div class="light x10"></div>
            <div class="light x11"></div>
            <div class="light x12"></div>
            <div class="light x13"></div>
            <div class="light x14"></div>
            <div class="light x15"></div>
            <div class="light x16"></div>
            <div class="light x17"></div>
            <div class="light x18"></div>
            <div class="light x19"></div>
            <div class="light x20"></div>
            <div class="light x21"></div>
            <div class="light x22"></div>
            <div class="light x23"></div>
            <div class="light x24"></div>
            <div class="light x25"></div>
            <div class="light x26"></div>
            <div class="light x27"></div>
            <div class="light x28"></div>
            <div class="light x29"></div>
            <div class="light x30"></div>
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
