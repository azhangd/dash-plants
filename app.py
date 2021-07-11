import json
from urllib.request import urlopen

import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output

this_directory = os.path.dirname(__file__)
src_zip_zones = os.path.join(this_directory, 'data', 'zip_zones.csv')
src_usda_plants = os.path.join(this_directory, 'data', 'usda_plants_20160223.csv')

df = pd.read_csv(src_zip_zones)
df['min_temp'] = df['trange'].apply(lambda x: x.split(' ')[0])
df['min_temp'] = pd.to_numeric(df['min_temp'])

df_plants = pd.read_csv(src_usda_plants)

df_plants.drop_duplicates()
df_plants['id'] = df_plants.index

df_plants = df_plants.filter(
    items=[
        'id',
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

df_plants.head()

px.set_mapbox_access_token("pk.eyJ1IjoiYmlnZG9nZGF0YSIsImEiOiJja3FiYnd2MWcwaDF1Mm9rZDhpNGVqc2gzIn0.XeBuYQMlGHgu4ml4R4RtRQ")

colors = {
    'background': 'rgba(0,0,0,0)',
    'text': 'white'
}

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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

PAGE_SIZE = 20

app = dash.Dash(
    __name__,
    meta_tags=[
            {
                "name": "viewport",
                "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
            }
    ],
)

server = app.server

'''
########################## APP LAYOUT ##########################
'''

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Plant Hardiness Dashboard",
                            style={"margin-bottom": "0px"},
                        )
                    ],
                    className="one-half column",
                    id="title"
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Source Code", id="learn-more-button"),
                            href="https://github.com/azhangd/dash-plant-hardiness",
                        )
                    ],
                    id="button"
                )
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"}
        ),

        html.Div(
            [
                html.Div(
                    [         
                        html.Label('Scientific Name'),

                        dcc.Dropdown(
                            id='plants-dropdown',
                            options=[{'label': i, 'value': i} for i in df_plants['scientific_name']],
                            value=[],
                            multi=True,
                            className="dcc_control"
                        ),

                        dcc.Graph(
                            id='plants-map'
                        ),

                    ], 
                    className="pretty_container eight columns"
                ),

                html.Div(
                    [         
                        daq.LEDDisplay(
                            id='led-zipcode',
                            value="00000",
                            label='zipcode',
                            backgroundColor='transparent'
                        ),

                        html.Div(
                            [
                                # dash_table.DataTable(
                                #     id='table-paging-and-sorting',
                                #     columns=[
                                #         {'name': i, 'id': i, 'deletable': True} for i in df_plants.columns
                                #     ],
                                #     page_current=0,
                                #     page_size=PAGE_SIZE,
                                #     page_action='custom',

                                #     sort_action='custom',
                                #     sort_mode='single',
                                #     sort_by=[],
                                #     style_data_conditional=[                
                                #         {
                                #             "if": {"state": "active"},  # 'active' | 'selected'
                                #             "backgroundColor": "#525F89",
                                #             "border": "#FFFFF"
                                #             # "border": "1px solid blue"
                                #         }
                                #     ],
                                #     style_cell={
                                #         'backgroundColor': colors['background'],
                                #         'color': colors['text'],
                                #         'textAlign': 'right'
                                #     },
                                #     style_as_list_view=True,
                                #     css=[
                                #         {
                                #             'selector': 'tr:hover', 
                                #             'rule': 'background-color: #525F89;'
                                #         }
                                #     ],
                                #     tooltip_data=[
                                #         {
                                #             column: {
                                #                 'value': 'Location at Big Bear Lake\n\n![Big Bear Lake](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Big_Bear_Valley%2C_California.jpg/1200px-Big_Bear_Valley%2C_California.jpg)', 
                                #                 # 'value': 
                                #                 'type': 'markdown'
                                #                 }
                                #             # column: {'value': get_image(value), 'type': 'markdown'}
                                #             for column, value in row.items()
                                #         } for row in df_plants.to_dict('records')
                                #     ],
                                # ),
                                # dash_table.DataTable(
                                #     id='output',
                                #     columns=[
                                #         {'name': i, 'id': i} for i in sorted(df_plants.columns)
                                #     ],
                                # )
                            ],
                        ),
                        
                        # dcc.Markdown(
                        #     """
                        #     **Click Data**
                        #     Click on points in the graph."""
                        # ),
                    
                        # html.Pre(id='click-data', style=styles['pre']),
                    ],
                    id="right-column",
                    className="pretty_container five columns"
                ),
            ],
            className="row flex-display"
        ),

        html.Div(
            [
                html.Div(
                    [         
                        dash_table.DataTable(
                            id='table-paging-and-sorting',
                            columns=[
                                {'name': i, 'id': i, 'deletable': True} for i in df_plants.columns
                            ],
                            page_current=0,
                            page_size=PAGE_SIZE,
                            page_action='custom',

                            sort_action='custom',
                            sort_mode='single',
                            sort_by=[],
                            style_data_conditional=[                
                                {
                                    "if": {"state": "active"},  # 'active' | 'selected'
                                    "backgroundColor": "#525F89",
                                    "border": "#FFFFF"
                                    # "border": "1px solid blue"
                                }
                            ],
                            style_cell={
                                'backgroundColor': colors['background'],
                                'color': colors['text'],
                                'textAlign': 'right'
                            },
                            style_as_list_view=True,
                            css=[
                                {
                                    'selector': 'tr:hover', 
                                    'rule': 'background-color: #525F89;'
                                }
                            ],
                            # tooltip_data=[
                            #     {
                            #         column: {
                            #             'value': 'Location at Big Bear Lake\n\n![Big Bear Lake](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Big_Bear_Valley%2C_California.jpg/1200px-Big_Bear_Valley%2C_California.jpg)', 
                            #             # 'value': 
                            #             'type': 'markdown'
                            #             }
                            #         # column: {'value': get_image(value), 'type': 'markdown'}
                            #         for column, value in row.items()
                            #     } for row in df_plants.to_dict('records')
                            # ],
                        ),
                    ], 
                    className="pretty_container five columns"
                ),

                html.Div(
                    [
                        html.Img(id="image-url")
                    ]
                )

            ],
            className="row flex-display"
        )

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"}
)

'''
########################## HELPER FUNCTIONS ##########################
'''

def filter_df_plants(selected_plant):
    df_plants_filtered = df_plants[df_plants['scientific_name'].isin(selected_plant)]
    selected_temp = df_plants_filtered['min_temp'].max()
    filtered_df = df[df['min_temp'] >= selected_temp]
    return filtered_df

def get_image_url(selected_plant):
    url_1 = 'https://plants.sc.egov.usda.gov/ImageLibrary/standard/'
    url_2 = '_001_svp.jpg'
    symbol = df_plants[df_plants['scientific_name']==selected_plant]['symbol'].to_string(index=False)
    # print(symbol)
    # url = df_plants.query('scientific_name = @selected_plant')['symbol']
    # print('url_1 = ' + url_1)
    # print('symbol = ' + symbol)
    # print('url_2 = ' + url_2)
    # print(url_1 + symbol + url_2)
    return(url_1 + symbol + url_2)

                
'''
########################## CALLBACKS ##########################
'''


@app.callback(
    Output('plants-map', 'figure'),
    Input('plants-dropdown', 'value')
)
def update_graph(selected_plant):
    if selected_plant is None:
        return dash.no_update
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

'''
# Scattermap click data
'''
# @app.callback(
#     Output('click-data', 'children'),
#     Input('plants-map', 'clickData'))
# def display_click_data(clickData):
#     if clickData is None:
#         return 'none'
#     else:
#         return json.dumps(clickData['points'][0]['customdata'], indent=2)

@app.callback(
    Output('table-paging-and-sorting', 'data'),
    Input('table-paging-and-sorting', "page_current"),
    Input('table-paging-and-sorting', "page_size"),
    Input('table-paging-and-sorting', 'sort_by'))
def update_table(page_current, page_size, sort_by):
    if len(sort_by):
        df_plants_filtered = df_plants.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    else: 
        # No sort is applied
        df_plants_filtered = df_plants

    return df_plants_filtered.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')

@app.callback(
    # Output("output", "data"), 
    Output("image-url", "src"), 
    Input("table-paging-and-sorting", "active_cell")
)
def cell_clicked(active_cell):
    if active_cell is None:
        return dash.no_update

    row = active_cell["row_id"]
    col = active_cell["column_id"]
    selected_plant = df_plants.at[row, col]
    # df_selected_plant= df_plants[df_plants['scientific_name'] == selected_plant],
    # df_selected_plant= df_plants.query('scientific_name==@selected_plant')
    # print(df_selected_plant)
    # fig = dash_table.DataTable(
    #     columns=[
    #         {'name': i, 'id': i} for i in sorted(df_selected_plant.columns)
    #     ],
    #     data=df_selected_plant.to_dict("records"),
    #     export_format="csv"
    # )
    # return fig
    print(str(get_image_url(selected_plant)))
    return str(get_image_url(selected_plant))


app.run_server(debug=True, use_reloader=False)