import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Import the data
df = pd.read_csv('Data_Processed.csv')

hourly_counts = pd.read_csv('assets/hourly_counts.csv')
post_covid = pd.read_csv('assets/post_covid.csv')
county_counts = pd.read_csv('assets/county_counts.csv')
monthly_counts = pd.read_csv('assets/monthly_counts.csv')
daily_counts = pd.read_csv('assets/daily_counts.csv')


# Create the Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1("Annapolis Car Crash Analysis", style={'display': 'inline-block'}),
        html.Img(src=app.get_asset_url('maryland.png'), style={'position': 'absolute', 'right': '0', 'top': '0'})
    ]),

html.P(

"This dashboard uses python's plotly dash to show car crashes trends in Maryland over the last several years." 
"Data on from Maryland. https://opendata.maryland.gov/Public-Safety/Maryland-Statewide-Vehicle-Crashes/65du-s3qu"  
"Check out the code at https://github.com/ballard11/Maryland_DS"
        , style={"margin": "20px"}),

    
    html.Div([
        dcc.Dropdown(
            id='map-dropdown',
            options=[{'label': i, 'value': i} for i in df['REPORT_TYPE'].dropna().unique()],
            value='Fatal Crash',
            style={'width': '50%'}
        ),
        dcc.Graph(id='map-graph')
    ]),

  html.Div([
    dcc.Dropdown(
        id='county-dropdown',
        options=[{'label': i, 'value': i} for i in df['COUNTY_DESC'].dropna().unique()],
        value='Anne Arundel',
        style={"width": "50%"}
    ),
]),
html.Div([  # Container for the hourly graph
    dcc.Graph(id='hourly-graph')
], style={"width": "33%", "float": "left"}),
html.Div([  # Container for the day graph
    dcc.Graph(id='day-graph')
], style={"width": "33%", "float": "left"}),
html.Div([  # Container for the monthly graph
    dcc.Graph(id='monthly-graph')
], style={"width": "33%", "float": "left"}),


    html.Div([
        html.H2("COVID-19 Crash Analysis"),
        dcc.Graph(id='covid-graph')
    ])
])


@app.callback(
    [Output('hourly-graph', 'figure'),
     Output('day-graph', 'figure'),
     Output('monthly-graph', 'figure')],
    [Input('county-dropdown', 'value')]
)
def update_graphs(County):
    # Hourly graph update
    filtered_df_hourly = hourly_counts[hourly_counts['COUNTY_DESC'] == County]
    fig_hourly = px.line(filtered_df_hourly, x='HOUR', y='COUNT', color='REPORT_TYPE', title='Hourly Trend in Crashes')
    fig_hourly.update_layout(legend=dict(
        yanchor="top",
        y=1,
        xanchor="right",
        x=1,
        bgcolor='rgba(255,255,255,0.1)'
    ))

    # Day graph update
    filtered_df_day = daily_counts[daily_counts['COUNTY_DESC'] == County]
    fig_day = px.line(filtered_df_day, x='DAY', y='COUNT', color='REPORT_TYPE', title='Daily Trend in Crashes')
    fig_day.update_layout(legend=dict(
        yanchor="top",
        y=1,
        xanchor="right",
        x=1,
        bgcolor='rgba(255,255,255,0.1)'
    ))

    # Monthly graph update
    filtered_df_monthly = monthly_counts[monthly_counts['COUNTY_DESC'] == County]
    fig_monthly = px.bar(filtered_df_monthly, x='MONTH', y='COUNT', color='REPORT_TYPE', title='Monthly Trend in Crashes')
    fig_monthly.update_layout(legend=dict(
        yanchor="top",
        y=1,
        xanchor="right",
        x=1,
        bgcolor='rgba(255,255,255,0.1)'
    ))

    return fig_hourly, fig_day, fig_monthly

    
#COVID Crash Analysis
@app.callback(
    Output('covid-graph', 'figure'),
    [Input('map-dropdown', 'value')])
def update_covid_graph(dummy_input):
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
        width=1600,
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
