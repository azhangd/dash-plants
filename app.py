import json
from urllib.request import urlopen

import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output

df = pd.read_csv('./data/zip_zones.csv')
df['min_temp'] = df['trange'].apply(lambda x: x.split(' ')[0])
df['min_temp'] = pd.to_numeric(df['min_temp'])

df_plants = pd.read_csv('./data/usda_plants_20160223.csv', engine='python')

df_plants.drop_duplicates()

df_plants = df_plants.filter(
    items=[
        'Symbol',
        'Scientific Name.x',
        'Common Name'
        'Species',
        'Growth Habit',
        'Temperature, Minimum (°F)',
        'Bloom Period',
        'Salinity Tolerance',
        'Shade Tolerance'
    ]
)

df_plants = df_plants.rename(
    columns={
        "Symbol": "symbol",
        "Scientific Name.x": "scientific_name",
        "Common Name": "common_name",
        "Species": "species", "Growth Habit": "growth_habit",
        "Temperature, Minimum (°F)": "min_temp",
        "Bloom Period": "bloom_period",
        "Salinity Tolerance": "salinity_tolerance",
        "Shade Tolerance": "shade_tolerance",
    }
)

df_plants = df_plants[df_plants['min_temp'].notnull()]

px.set_mapbox_access_token("pk.eyJ1IjoiYmlnZG9nZGF0YSIsImEiOiJja3FiYnd2MWcwaDF1Mm9rZDhpNGVqc2gzIn0.XeBuYQMlGHgu4ml4R4RtRQ")

colors = {
    'background': 'rgba(0,0,0,0)',
    'text': 'white'
}

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = [dbc.themes.DARKLY]

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}


app = dash.Dash(
    __name__,
    meta_tags=[
            {
                "name": "viewport",
                "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
            }
    ],
)

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(html.Tr([html.Th(col) for col in dataframe.columns])),
        html.Tbody([html.Tr([html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])
                   for i in range(min(len(dataframe), max_rows))])
    ])


'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~ APP LAYOUT ~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

app.layout = html.Div([
    html.Div(
        [
            html.Div(
                [
                    html.H1(
                        "Plant Hardiness Dashboard",
                        style={"margin-bottom": "0px"},
                    )
                ],
                className="seven columns",
                id="title"
            ),
            html.Div(
                [
                    html.A(
                        html.Button("Source Code", id="learn-more-button"),
                        href="https://plot.ly/dash/pricing/",
                    )
                ],
                className="seven columns",
                id="button"
            )
        ],
        id="header",
        className="row flex-display",
        style={"margin-bottom": "25px"}
    ),

    html.Div([
        html.Div([         
            html.Label('Scientific Name'),

            # daq.Thermometer( 
            #     id='temperature',
            #     value=0,
            #     label="Temperature", 
            #     max=65, 
            #     min=-55, 
            #     showCurrentValue=True, 
            #     units="F", 
            #     color='red'
            # ),

            dcc.Dropdown(
                id='plants-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['scientific_name']],
                value=[],
                multi=True
                # style=dict(background='#1c2545')
            ),

            dcc.Graph(
                id='plants-map',
            ),

        ], className="pretty_container seven columns"),

    ], className="row"),

    html.Div(
        [
            dcc.Markdown(
                """
                **Click Data**
                Click on points in the graph."""
            ),

            html.Pre(id='click-data', style=styles['pre']),

            daq.LEDDisplay(
                id='led-zipcode',
                value="00000",
                label='zipcode',
                backgroundColor='transparent'
            ),
        ],
        className="pretty_container seven columns"
    )
])

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~ APP METHODS ~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''


def filter_df_plants(selected_plant):
    df_plants_filtered = df_plants[df_plants['scientific_name'].isin(selected_plant)]
    selected_temp = df_plants_filtered['min_temp'].max()
    filtered_df = df[df['min_temp'] >= selected_temp]
    return filtered_df

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~ APP CALLBACKS ~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

@app.callback(
    Output('plants-map', 'figure'),

    Input('plants-dropdown', 'value')
)
def update_graph(selected_plant):
    if not selected_plant:
        filtered_df = df
    else:
        filtered_df = filter_df_plants(selected_plant)

    fig = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        hover_name="city",
        hover_data=["zone", "zipcode"],
        color="min_temp",
        color_continuous_scale=px.colors.sequential.haline,
        range_color=[-55, 65],
        center={"lat": 37.0902, "lon": -95.7129},
        zoom=4.5,
        opacity=0.8
    )

    fig.update_layout(
        legend_title_text='Min. Temp',
        mapbox_style="mapbox://styles/bigdogdata/ckqreebqs3s2b17rygkmnnyhy/draft",
        # mapbox_style="mapbox://styles/plotlymapbox/cjvppq1jl1ips1co3j12b9hex",

        autosize=True,
        uirevision='no reset of zoom',
        margin=dict(l=30, r=30, b=20, t=0),
        #margin=dict(t=0, b=0, l=0, r=0),
        height=1000,
        #width = 1920,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        legend_bgcolor=colors['background'],
        font_color=colors['text']
    )

#     table_fig = dash_table.DataTable(
#         columns=[{"name": i, "id": i} for i in df_plants_filtered.columns],
#         data=df_plants_filtered,
#         style_cell=dict(textAlign='left'),
#         style_header=dict(backgroundColor="paleturquoise"),
#         style_data=dict(backgroundColor="lavender")
#     )

    return fig
# , table_fig


@app.callback(
    Output('led-zipcode', 'value'),
    Input('plants-map', 'clickData'))
def display_click_data(clickData):
    if clickData is None:
        return '00000'
    else:
        return clickData['points'][0]['customdata'][1]

@app.callback(
    Output('click-data', 'children'),
    Input('plants-map', 'clickData'))
def display_click_data(clickData):
    if clickData is None:
        return 'none'
    else:
        return json.dumps(clickData['points'][0]['customdata'], indent=2)

# @app.callback(
#     Output('temperature', 'value'),
#     Input('plants-map', 'clickData'))
# def display_click_data(clickData):
#     if clickData is None:
#         return 0
#     else:
#         click_zip = clickData['points'][0]['customdata'][1]
#         print(df[['zipcode']==click_zip]['min_temp'])
#         return df[['zipcode']==click_zip]['min_temp']

app.run_server(debug=True, use_reloader=False)
