import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Import the data
df = pd.read_csv('C:\\Users\\Ben\\OneDrive\\Documents\\Maryland_Statewide_Vehicle_Crashes.csv')

# Convert ACC_DATE to datetime format
df['ACC_DATE'] = pd.to_datetime(df['ACC_DATE'], format='%Y%m%d')

# Combine ACC_DATE and ACC_TIME into a single datetime column
df['ACC_DATETIME'] = pd.to_datetime(df['ACC_DATE'].astype(str) + ' ' + df['ACC_TIME'])

# Extract hour and month from ACC_DATETIME
df['HOUR'] = df['ACC_DATETIME'].dt.hour
df['MONTH'] = df['ACC_DATETIME'].dt.month

# Pre-compute the data for the plots
hourly_counts = df.groupby(['HOUR', 'REPORT_TYPE']).size().unstack(fill_value=0).reset_index()
county_counts = df.groupby(['COUNTY_DESC', 'REPORT_TYPE']).size().unstack(fill_value=0).reset_index()

# Create the Dash app
app = dash.Dash(__name__)
server = app.server


# Define the app layout
app.layout = html.Div([
    html.H1("Crash Analysis Dashboard"),
    
    html.Div([
        dcc.Graph(id='hourly-graph'),
        dcc.Dropdown(
            id='hourly-dropdown',
            options=[{'label': i, 'value': i} for i in df['REPORT_TYPE'].dropna().unique()],
            value='Property Damage Crash'
        )
    ]),
    
    html.Div([
        dcc.Graph(id='county-graph'),
        dcc.Dropdown(
            id='county-dropdown',
            options=[{'label': i, 'value': i} for i in df['REPORT_TYPE'].dropna().unique()],
            value='Property Damage Crash'
        )
    ])
])

# Define the app callbacks
@app.callback(
    Output('hourly-graph', 'figure'),
    Input('hourly-dropdown', 'value'))
def update_hourly_graph(crash_type):
    filtered_df = hourly_counts[['HOUR', crash_type]]
    fig = px.line(filtered_df, x='HOUR', y=crash_type, title='Hourly Trend in Crashes')
    return fig

@app.callback(
    Output('county-graph', 'figure'),
    Input('county-dropdown', 'value'))
def update_county_graph(crash_type):
    filtered_df = county_counts[['COUNTY_DESC', crash_type]]
    fig = px.bar(filtered_df, x='COUNTY_DESC', y=crash_type, title='County-wise Distribution of Crashes')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)

