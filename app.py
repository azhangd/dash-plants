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
from flask.helpers import get_root_path
print(get_root_path(__name__))

# Get relative data paths
this_directory = os.path.dirname(__file__)
src_zip_zones = os.path.join(this_directory, 'data', 'zip_zones.csv')
src_usda_plants = os.path.join(this_directory, 'data', 'usda_plants_filtered.csv')

# Load data
df = pd.read_csv(src_zip_zones)
df_plants = pd.read_csv(src_usda_plants)

# Get minimum temperature from trange
df['min_temp'] = df['trange'].apply(lambda x: x.split(' ')[0])
df['min_temp'] = pd.to_numeric(df['min_temp'])

# Fix column names
df_plants.columns = df_plants.columns.str.lower()

# Sort dataframe
df_plants = df_plants.sort_values('common_name')
df_plants = df_plants.reset_index(drop=True)

# Insert row id to df_plants
df_plants.insert(loc=0, column='id', value=np.arange(len(df_plants)))

# Set mapbox access token
px.set_mapbox_access_token("pk.eyJ1IjoiYmlnZG9nZGF0YSIsImEiOiJja3FiYnd2MWcwaDF1Mm9rZDhpNGVqc2gzIn0.XeBuYQMlGHgu4ml4R4RtRQ")

# Style settings
colors = {
    'background': 'rgba(0,0,0,0)',
    'text': 'white'
}

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
app.title = 'Plants Lookup'
server = app.server

# App layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Plant Finder",
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
                            href="https://github.com/azhangd/dash-plants",
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
                        html.Div(
                            [   
                                html.Label('Zip Code'),
                                dcc.Dropdown(
                                    id='zip-dropdown',
                                    options=[{'label': i, 'value': i} for i in df['zipcode']],
                                    value=92620,
                                    multi=False,
                                    placeholder="Zip Code",
                                    className="dcc_control"
                                ),

                                html.P('Filter by duration:'),

                                dcc.Checklist(
                                    id='checklist-duration',
                                    options=[
                                        {'label': 'Biennial', 'value': 'Biennial'},
                                        {'label': 'Annual', 'value': 'Annual'},
                                        {'label': 'Perennial', 'value': 'Perennial'}
                                    ],
                                    labelStyle={'display': 'inline-block'},
                                    style={
                                        'color': 'white'
                                        # 'font-size': '25px'
                                    }
                                ),

                                dcc.Checklist(
                                    id='checklist-image',
                                    options=[
                                        {'label': 'Has Image?', 'value': 'Yes'}
                                    ],
                                    value=['Yes']
                                ),                              

                                dash_table.DataTable(
                                    id='table-paging-and-sorting',
                                    columns=[
                                        # {'name': i, 'id': i, 'deletable': True} for i in df_plants.columns
                                        {'name': 'Common Name', 'id': 'common_name'},
                                        # {'name': 'Growth Habit', 'id': 'growth_habit'},
                                        # {'name': 'Duration', 'id': 'duration'},
                                        # {'name': 'Minimum Temp. (F)', 'id': 'temperature_minimum_f'}
                            
                                    ],
                                    data=df_plants[df_plants['temperature_minimum_f'] <= 30].to_dict('records'),
                                    page_size=50,
                                    style_table={'height': '700px', 'overflowY': 'auto'},
                                    style_header={'backgroundColor': '#525F89'},
                                    style_data_conditional=[                
                                        {
                                            'if': {'state': 'active'},  # 'active' | 'selected'
                                            'backgroundColor': '#525F89',
                                            'border': '#FFFFF'
                                            # "border": "1px solid blue"                                    
                                        },
                                        {
                                            'if': {'column_id': 'common_name'},
                                            'textAlign': 'center'
                                        }
                                    ],
                                    style_header_conditional=[
                                        {
                                            'if': {'column_id': 'common_name'},
                                            'textAlign': 'center'
                                        }
                                    ],
                                    style_cell={
                                        'backgroundColor': colors['background'],
                                        'color': colors['text'],
                                        'textAlign': 'left'
                                    },
                                    style_as_list_view=True,
                                    css=[
                                        {
                                            'selector': 'tr:hover', 
                                            'rule': 'background-color: #525F89;'
                                        }
                                    ],
                                    # fill_width=False
                                ),

                                # html.Br(),
                                # dcc.Checklist(
                                #     id='datatable-use-page-count',
                                #     options=[
                                #         {'label': 'Use page_count', 'value': 'True'}
                                #     ],
                                #     value=['True']
                                # ),
                                # 'Page count: ',
                                # dcc.Input(
                                #     id='datatable-page-count',
                                #     type='number',
                                #     min=1,
                                #     max=29,
                                #     value=20
                                # ),
                            ], 
                            # className="five columns"
                        ),
                    ],
                    className="pretty_container two columns"                   
                ),



                html.Div(
                    [
                        html.Div(
                            id='common_scientific_div',
                            children=[
                                html.Label('Common Name'),
                                dcc.Dropdown(
                                    id='common-dropdown',
                                    options=[{'label': i, 'value': i} for i in df_plants['common_name']],
                                    value=['clasping arnica'],
                                    multi=True,
                                    className="dcc_control"
                                ),
                                html.P(children='OR', style={'text-align': 'center'}),
                                html.Label('Scientific Name'),
                                dcc.Dropdown(
                                    id='scientific-dropdown',
                                    options=[{'label': i, 'value': i} for i in df_plants['scientific_name_x']],
                                    value=['Arnica amplexicaulis Nutt.'],
                                    multi=True,
                                    className="dcc_control"
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.Img(
                                    id="image-url", 
                                    src='https://plants.sc.egov.usda.gov/ImageLibrary/standard/ARAM2_001_svp.jpg',
                                    style={
                                        'height': '50%',
                                        'width': '50%',
                                        'marginTop': '30px',
                                        'marginBottom': '30px'
                                    }
                                )
                            ],
                            style={'textAlign': 'center'}
                        ),
                    ],
                    id="middle-column",
                    className="pretty_container four columns"                   
                ),

                html.Div(
                    [
                        dcc.Graph(
                            id='plants-map'
                        ),
                        # daq.LEDDisplay(
                        #     id='led-zipcode',
                        #     value="92620",
                        #     label='Your Zipcode:',
                        #     backgroundColor='transparent'
                        # ),
                    ], 
                    id="right-column",
                    className="pretty_container five columns"
                ),
            ],
            className="row flex-display"
        ),

        html.Div(
            [
                # html.Div(
                #     [   
                #         # dash_table.DataTable(
                #         #     id='table-paging-and-sorting',
                #         #     columns=[
                #         #         {'name': i, 'id': i, 'deletable': True} for i in df_plants.columns
                #         #     ],
                #         #     page_current=0,
                #         #     page_size=PAGE_SIZE,
                #         #     page_action='custom',

                #         #     sort_action='custom',
                #         #     sort_mode='single',
                #         #     sort_by=[],
                #         #     style_data_conditional=[                
                #         #         {
                #         #             "if": {"state": "active"},  # 'active' | 'selected'
                #         #              "backgroundColor": "#525F89",
                #         #             "border": "#FFFFF"
                #         #             # "border": "1px solid blue"
                #         #         }
                #         #     ],
                #         #     style_cell={
                #         #         'backgroundColor': colors['background'],
                #         #         'color': colors['text'],
                #         #         'textAlign': 'right'
                #         #     },
                #         #     style_as_list_view=True,
                #         #     css=[
                #         #         {
                #         #             'selector': 'tr:hover', 
                #         #             'rule': 'background-color: #525F89;'
                #         #         },
                #         #     ],
                #         #     fill_width=False
                #         # ),

                #         # html.Br(),
                #         # dcc.Checklist(
                #         #     id='datatable-use-page-count',
                #         #     options=[
                #         #         {'label': 'Use page_count', 'value': 'True'}
                #         #     ],
                #         #     value=['True']
                #         # ),
                #         # 'Page count: ',
                #         # dcc.Input(
                #         #     id='datatable-page-count',
                #         #     type='number',
                #         #     min=1,
                #         #     max=29,
                #         #     value=20
                #         # ),
                #     ], 
                #     className="pretty_container"
                # ),
            ],
            className="row flex-display"
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"}
)

# Helper Functions
def filter_df_plants(selected_plant):
    df_plants_filtered = df_plants[df_plants['common_name'].isin(selected_plant)]
    selected_temp = df_plants_filtered['temperature_minimum_f'].max()
    filtered_df = df[df['min_temp'] >= selected_temp]
    return filtered_df

def get_image_url(selected_plant):
    url_1 = 'https://plants.sc.egov.usda.gov/ImageLibrary/standard/'
    url_2 = '_001_svp.jpg'
    symbol = df_plants[df_plants['common_name']==selected_plant]['symbol'].to_string(index=False)
    return (url_1 + symbol + url_2)

def filter_by_zip(selected_df, selected_zip):
    min_temp = df[df['zipcode'] == selected_zip]['min_temp'].item()
    return selected_df[selected_df['temperature_minimum_f'] <= min_temp]

def filter_by_duration(selected_df, duration_list):
    for duration in duration_list:
        selected_df = selected_df[selected_df['duration'].str.contains(duration, case=False, na=False)]
    return selected_df

def filter_by_image(selected_df):
    return selected_df[selected_df['has_image'] > 0]

# Update map with dropdown
@app.callback(
    Output('plants-map', 'figure'),
    Input('common-dropdown', 'value')
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
    return fig
  
# Show zip code on map click
@app.callback(
    # Output('led-zipcode', 'value'),
    Output('zip-dropdown', 'value'),
    Input('plants-map', 'clickData')
    )
def display_click_data(clickData):
    if clickData is None:
        return dash.no_update
    else:
        return clickData['points'][0]['customdata'][1]

# # Change pages in datatable
# @app.callback(
#     Output('table-paging-and-sorting', 'data'),
#     Input('table-paging-and-sorting', "page_current"),
#     Input('table-paging-and-sorting', "page_size"),
#     Input('table-paging-and-sorting', 'sort_by'),
#     Input('zip-dropdown', 'value')
# )
# def update_table(page_current, page_size, sort_by):
#     if len(sort_by):
#         df_plants_filtered = df_plants.sort_values(
#             sort_by[0]['column_id'],
#             ascending=sort_by[0]['direction'] == 'asc',
#             inplace=False
#         )
#     else: 
#         # No sort is applied
#         df_plants_filtered = df_plants
#     return df_plants_filtered.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')

# # Filter datatable by zip code
# @app.callback(
#     Output('table-paging-and-sorting', 'data'),
#     # Output('test', 'children'),
#     Input('zip-dropdown', 'value')
# )
# def update_table(selected_zip):
#     print(selected_zip)
#     if selected_zip is None:
#         return dash.no_update
#     else:
#         # print(filter_by_zip(selected_zip))
#         return filter_by_zip(selected_zip).to_dict('records')

# Update table using zip dropdown
@app.callback(
        Output('table-paging-and-sorting', 'data'),
        Input('zip-dropdown', 'value'), 
        Input("checklist-duration", "value"),
        Input("checklist-image", "value")
)   
def update_table(selected_zip, duration_list, image_selected_list):
    data = df_plants
    if selected_zip and duration_list and image_selected_list is None:  
        return data.to_dict('records')
    if selected_zip is not None:
        data = filter_by_zip(data, selected_zip)
    if duration_list is not None:
        data = filter_by_duration(data, duration_list)
    if image_selected_list:
        print(image_selected_list)
        print(type(image_selected_list))
        print('filtering by image')
        data = filter_by_image(data)
    return data.to_dict('records')


    # table = dash_table.DataTable(
    #     id='table-paging-and-sorting',
    #     columns=[
    #         {'name': 'Common Name', 'id': 'common_name'},
    #         {'name': 'Minimum Temp.', 'id': 'temperature_minimum_f'}                                        
    #     ],
    #     # data=data,
    #     page_size=50,
    #     style_table={'height': '1000px', 'overflowY': 'auto'},
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
    #     # style_as_list_view=True,
    #     css=[
    #         {
    #             'selector': 'tr:hover', 
    #             'rule': 'background-color: #525F89;'
    #         },
    #     ],
    #     # fill_width=False
    # )
    # return table

# @app.callback(
#     Output('table-paging-and-sorting', 'data'),
#     [
#         # Input('table-paging-and-sorting', "page_current"),
#         # Input('table-paging-and-sorting', "page_size"),
#         # Input('table-paging-and-sorting', 'sort_by'),
#         Input('zip-dropdown', 'value')
#     ]
# )
# # def input_update(page_current, page_size, sort_by, selected_zip):
# def input_update(selected_zip):
#     trigger_id = dash.callback_context.triggered[0]["prop_id"]

#     if trigger_id == "zip-dropdown.value":
#         print(selected_zip)
#         if selected_zip is None:
#             return dash.no_update
#         else:
#             # print(filter_by_zip(selected_zip))
#             return filter_by_zip(selected_zip).to_dict('records')
    # else:
    #     if len(sort_by):
    #         df_plants_filtered = df_plants.sort_values(
    #             sort_by[0]['column_id'],
    #             ascending=sort_by[0]['direction'] == 'asc',
    #             inplace=False
    #         )
    #     else: 
    #         # No sort is applied
    #         df_plants_filtered = df_plants
    #     return df_plants_filtered.iloc[page_current*page_size:(page_current+ 1)*page_size].to_dict('records')

# @app.callback(
#     Output('table-paging-and-sorting', 'page_count'),
#     Input('datatable-use-page-count', 'value'),
#     Input('datatable-page-count', 'value'))
# def update_table(use_page_count, page_count_value):
#     if len(use_page_count) == 0 or page_count_value is None:
#         return None
#     return page_count_value

# Show image on datatable click
@app.callback(
    Output("image-url", "src"), 
    Input("table-paging-and-sorting", "active_cell")
)
def cell_clicked(active_cell):
    trigger_id = dash.callback_context.triggered[0]["prop_id"]
    if trigger_id == 'table-paging-and-sorting.active_cell':
        if active_cell is None:
            return dash.no_update
        row_id = active_cell["row_id"]
        if df_plants.at[row_id, 'has_image'] > 0:
            selected_plant = df_plants.at[row_id, 'common_name']
            return str(get_image_url(selected_plant))
        else:
            return 'https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg'


# Add value to common/scientific dropdown when datatable is clicked
@app.callback(
    Output('common-dropdown', 'value'), 
    Input("table-paging-and-sorting", "active_cell"),
    prevent_initial_call=True
)
def update_dropdown(active_cell):
    if active_cell is None:
        return dash.no_update
    row_id = active_cell["row_id"]
    selected_plant = df_plants.at[row_id, 'common_name']
    return [selected_plant]

# Sync scientific and common dropdowns
@app.callback(
    Output('common_scientific_div', 'children'),
    [
        Input('common-dropdown', 'value'),
        Input('scientific-dropdown', "value")
    ],
    prevent_initial_call=True
)
def input_update(common, scientific):
    trigger_id = dash.callback_context.triggered[0]["prop_id"]

    if trigger_id == "common-dropdown.value":
        scientific_list = []
        for i in common:
            scientific = df_plants[df_plants['common_name'] == i]['scientific_name_x'].to_string(index=False)
            scientific_list.append(scientific)
        return [
            html.Label('Common Name'),
            dcc.Dropdown(
                id='common-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['common_name']],
                value=common,
                multi=True,
                className="dcc_control"
            ),
            html.P(children='OR', style={'text-align': 'center'}),
            html.Label('Scientific Name'),
            dcc.Dropdown(
                id='scientific-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['scientific_name_x']],
                value=scientific_list,
                multi=True,
                className="dcc_control"
            )
        ]

    if trigger_id == "scientific-dropdown.value":
        common_list = []
        if len(scientific) > 0:
            for i in scientific:
                common = df_plants[df_plants['scientific_name_x'] == i]['common_name'].to_string(index=False)
                common_list.append(common)
        return [
            html.Label(children='Common Name'),
            dcc.Dropdown(
                id='common-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['common_name']],
                value=common_list,
                multi=True,
                className="dcc_control"
            ),
            html.P(children='OR', style={'text-align': 'center'}),
            html.Label(children='Scientific Name'),
            dcc.Dropdown(
                id='scientific-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['scientific_name_x']],
                value=scientific,
                multi=True,
                className="dcc_control"
            )
        ]
    return dash.no_update

app.run_server(debug=True, use_reloader=False)