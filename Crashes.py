import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Import the data
df = pd.read_csv('DF_output.csv')

# Convert ACC_DATE to datetime format
df['ACC_DATE'] = pd.to_datetime(df['ACC_DATE'], format='%Y%m%d')

# Combine ACC_DATE and ACC_TIME into a single datetime column
df['ACC_DATETIME'] = pd.to_datetime(df['ACC_DATE'].astype(str) + ' ' + df['ACC_TIME'])

# Extract hour and month from ACC_DATETIME
df['HOUR'] = df['ACC_DATETIME'].dt.hour
df['MONTH'] = df['ACC_DATETIME'].dt.month

# Pre-compute the data for the plots
hourly_counts = df.groupby(['HOUR', 'COUNTY_DESC', 'REPORT_TYPE']).size().reset_index()
hourly_counts.columns = ['HOUR', 'COUNTY_DESC', 'REPORT_TYPE', 'COUNT']
county_counts = df.groupby(['COUNTY_DESC', 'REPORT_TYPE']).size().unstack(fill_value=0).reset_index()

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the app layout
app.layout = html.Div([
    html.H1("Maryland Car Crash Analysis"),
    
    html.Div([
        dcc.Dropdown(
            id='hourly-dropdown',
            options=[{'label': i, 'value': i} for i in df['REPORT_TYPE'].dropna().unique()],
            value='Property Damage Crash',
            style={"width": "50%"}
        ),
        dcc.Graph(id='hourly-graph')
    ]),
    
    html.Div([
        dcc.Dropdown(
            id='county-dropdown',
            options=[{'label': i, 'value': i} for i in df['REPORT_TYPE'].dropna().unique()],
            value='Property Damage Crash',
            style={"width": "50%"}
        ),
        dcc.Graph(id='county-graph')
    ]),
    
    html.Div([
        dcc.Dropdown(
            id='map-dropdown',
            options=[{'label': i, 'value': i} for i in df['REPORT_TYPE'].dropna().unique()],
            value='Property Damage Crash',
        style={'width': '75%'}
        ),
        dcc.Graph(id='map-graph')
    ])
])


# Define the app callbacks

#Hourly Crash
@app.callback(
    Output('hourly-graph', 'figure'),
    Input('hourly-dropdown', 'value'))
def update_hourly_graph(crash_type):
    filtered_df = hourly_counts[hourly_counts['REPORT_TYPE'] == crash_type]
    fig = px.line(filtered_df, x='HOUR', y='COUNT', color='COUNTY_DESC', title='Hourly Trend in Crashes')
    return fig

#County Crash
@app.callback(
    Output('county-graph', 'figure'),
    Input('county-dropdown', 'value'))
def update_county_graph(crash_type):
    if crash_type in county_counts.columns:  # Check if the selected crash type is a column in the DataFrame
        fig = px.bar(county_counts, x='COUNTY_DESC', y=crash_type, title='Crashes by County')
    else:  # If not, create an empty figure
        fig = px.bar(title='No data available for the selected crash type')
    return fig

#Map Crash
@app.callback(
    Output('map-graph', 'figure'),
    Input('map-dropdown', 'value'))
def update_map_graph(crash_type):
    df_filtered = df[df['REPORT_TYPE'] == crash_type]
    fig_map = px.scatter_mapbox(
        df_filtered,
        lat='LATITUDE',
        lon='LONGITUDE',
        color='REPORT_TYPE',
        color_continuous_scale=px.colors.cyclical.IceFire,
        title='Crash locations in Maryland',
        opacity=0.25,
        category_orders={'REPORT_TYPE': ['Fatal Crash', 'Injury Crash', 'Property Damage Crash', 'Unknown']}
    )

    fig_map.update_layout(
        mapbox_style="mapbox://styles/mapbox/light-v10",
        mapbox_accesstoken='pk.eyJ1IjoiYmVuZ2JhbGxhcmQiLCJhIjoiY2xrMWp6dXFmMDZzZDNocGJ3Zjh5amMwZiJ9.YGDUZddiJp0uKNBG68Dhlw'
    )
    return fig_map

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
