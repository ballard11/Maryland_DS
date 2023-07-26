import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Import the data
df = pd.read_csv('DF_Output_Processed.csv')

# Pre-compute the data for the plots
hourly_counts = df.groupby(['HOUR', 'COUNTY_DESC', 'REPORT_TYPE']).size().reset_index()
hourly_counts.columns = ['HOUR', 'COUNTY_DESC', 'REPORT_TYPE', 'COUNT']
county_counts = df.groupby(['COUNTY_DESC', 'REPORT_TYPE']).size().unstack(fill_value=0).reset_index()

#For Long Term Trends
daily_counts = df.groupby(['ACC_DATE', 'COUNTY_DESC']).size().reset_index()
daily_counts['ACC_DATE'] = pd.to_datetime(daily_counts['ACC_DATE'])
daily_counts.columns = ['ACC_DATE', 'COUNTY_DESC', 'COUNT']
daily_counts.reset_index(inplace=True)
daily_counts['day_of_year'] = daily_counts['ACC_DATE'].dt.dayofyear
pre_covid = daily_counts[daily_counts['ACC_DATE'] < '2020-03-1']
post_covid = daily_counts[daily_counts['ACC_DATE'] >= '2020-03-1']
pre_covid_avg = pre_covid.groupby('day_of_year')['COUNT'].mean()
post_covid = post_covid.merge(pre_covid_avg, on='day_of_year', how='left', suffixes=('_post', '_pre'))
post_covid['percentage_of_pre_covid'] = (post_covid['COUNT_post'] / post_covid['COUNT_pre']) * 100
post_covid['Day_of_Year'] = post_covid['ACC_DATE'].dt.dayofyear
post_covid['Year'] = post_covid['ACC_DATE'].dt.year
post_covid['percentage_of_pre_covid_smooth'] = post_covid['percentage_of_pre_covid'].rolling(window=30).mean()

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the app layout
app.layout = html.Div([
    html.Div([
        html.H1("Maryland Car Crash Analysis", style={'display': 'inline-block'}),
        html.Img(src=app.get_asset_url('maryland.png'), style={'position': 'absolute', 'right': '0', 'top': '0'})
    ]),
    
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
        style={'width': '50%'}
        ),
        dcc.Graph(id='map-graph')
    ]),
    html.Div([
        html.H2("COVID-19 Crash Analysis"),
        dcc.Graph(id='covid-graph')
    ])
    
])


## Define the app callbacks

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

#COVID Crash Analysis
@app.callback(
    Output('covid-graph', 'figure'),
    [Input('county-dropdown', 'value')])  # This input isn't used, but you can replace it as needed
def update_covid_graph(crash_type):  # This input isn't used, but you can replace it as needed
    # The graph creation steps go here
    fig = px.line(post_covid, x='Day_of_Year', y='percentage_of_pre_covid_smooth', color='Year',
                  title='30-Day Smoothed Daily Crashes as a Percentage of Pre-COVID Baseline')
    fig.add_shape(type='line', xref='paper', yref='y', x0=0, x1=1, y0=100, y1=100, line=dict(color='Red', dash='dot'))
    months_in_year = [i*30 for i in range(13)]
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', '']
    fig.update_xaxes(tickvals=months_in_year, ticktext=month_names)
    
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
        width=1000,
        height=800,
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
