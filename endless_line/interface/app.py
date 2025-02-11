
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

# Initialize the Dash app with any required external stylesheets
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://use.fontawesome.com/releases/v6.4.0/css/all.css',
    '/assets/style.css'
    ])

# Configure the app
app.config.suppress_callback_exceptions = True

# Make server available for deployment platforms
server = app.server
