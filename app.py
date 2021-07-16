import json
from urllib.request import urlopen

import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Div import Div
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
df_plants = pd.read_csv(src_usda_plants, index_col=0)

# Create minimum temperature column from trange
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
                                html.Label('Filter by Zip Code:', className="control_label"),
                                dcc.Dropdown(
                                    id='zip-dropdown',
                                    options=[{'label': i, 'value': i} for i in df['zipcode']],
                                    value=92620,
                                    multi=False,
                                    placeholder="Zip Code",
                                    className="dcc_control"
                                ),

                                html.Div(id='slider-temperature-output', className="control_label"),
                                dcc.Slider(
                                    id='slider-temperature',
                                    min=-70,
                                    max=52,
                                    value=-70,
                                    marks={
                                        -70: {'label': '-70°F'},
                                        52: {'label': '52°F'}
                                    },
                                    className="dcc_control"
                                ),
                                
                                html.Label('Filter by Duration:', className="control_label"),
                                dcc.Checklist(
                                    id='checklist-duration',
                                    options=[
                                        {'label': 'Biennial', 'value': 'Biennial'},
                                        {'label': 'Annual', 'value': 'Annual'},
                                        {'label': 'Perennial', 'value': 'Perennial'}
                                    ],
                                    labelStyle={'display': 'inline-block'},
                                    className="dcc_control"
                                ),

                                html.Label('Filter by Growth Habit:', className="control_label"),
                                dcc.Dropdown(
                                    id='dropdown-growth-habit',
                                    options=[
                                        {'label': 'Tree', 'value': 'Tree'},
                                        {'label': 'Shrub', 'value': 'Shrub'},
                                        {'label': 'Forb', 'value': 'Forb'},
                                        {'label': 'Herb', 'value': 'Herb'},
                                        {'label': 'Graminoid', 'value': 'Graminoid'},
                                        {'label': 'Vine', 'value': 'Vine'}
                                    ],
                                    multi=True,
                                    placeholder="Growth Habit",
                                    className="dcc_control"
                                ),

                                # html.P('Image:', className="control_label"),
                                # html.Hr(),
                                # dcc.Checklist(
                                #     id='checklist-image',
                                #     options=[
                                #         {'label': 'Has Image?', 'value': 'Yes'}
                                #     ],
                                #     value=['Yes'],
                                #     labelStyle={'display': 'inline-block'},
                                #     className="dcc_control"
                                # ),
                                html.Div(
                                    [
                                        html.Label('Has image?', style={'marginRight': '5px'}),
                                        daq.BooleanSwitch(
                                            id='checklist-image',
                                            on=True,
                                            # theme =  {'dark': True},
                                            # label='Has image:',
                                            color="#33ffe6",
                                            # className="button"
                                            style={'marginRight':'20px'}
                                        ),

                                        # html.Label('Has guide?', style={'marginRight': '5px'}),
                                        # daq.BooleanSwitch(
                                        #     on=True,
                                        #     # theme =  {'dark': True},
                                        #     # label='Has image:',
                                        #     color="#33ffe6",
                                        #     # className="button"
                                        #     # style={'textAlign':'right'}
                                        # ),    
                                    ],
                                    className='control_label row flex-display'
                                ),
                                
                                # html.Label('Has image:', className="control_label"),                 
                                # daq.BooleanSwitch(
                                #     id='checklist-image',
                                #     on=True,
                                #     # theme =  {'dark': True},
                                #     # label='Has image:',
                                #     color="#33ffe6",
                                #     className="button"
                                #     # style={'textAlign':'right'}
                                # ),
                                dash_table.DataTable(
                                    id='table-paging-and-sorting',
                                    columns=[
                                        {'name': 'Common Name', 'id': 'common_name'},
                                    ],
                                    page_size=50,
                                    style_table={'height': '500px', 'overflowY': 'auto', 'marginTop': '15px'},
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
                                    active_cell={'row': 3, 'column': 0, 'column_id': 'common_name', 'row_id': 36},
                                    css=[
                                        {
                                            'selector': 'tr:hover', 
                                            'rule': 'background-color: #525F89;'
                                        }
                                    ],
                                ),
                            ], 
                        ),
                    ],
                    className="pretty_container two columns"                   
                ),

                html.Div(
                    [
                        # html.Div(
                        #     [
                                html.Div(
                                    id='common_scientific_div',
                                    children=[
                                        html.Label('Common Name', className='control_label'),
                                        dcc.Dropdown(
                                            id='common-dropdown',
                                            options=[{'label': i, 'value': i} for i in df_plants['common_name']],
                                            value='Amur honeysuckle',
                                            multi=False,
                                            className="dcc_control"
                                        ),
                                        html.Label('Scientific Name', className='control_label'),
                                        dcc.Dropdown(
                                            id='scientific-dropdown',
                                            options=[{'label': i, 'value': i} for i in df_plants['scientific_name_x']],
                                            value='Lonicera maackii (Rupr.) Herder',
                                            multi=False,
                                            className="dcc_control"
                                        )
                                    ],
                                ),
                                html.Div(
                                    [
                                        dcc.Loading(
                                            children=[
                                                html.Img(
                                                    id='image-url', 
                                                    src='https://plants.sc.egov.usda.gov/ImageLibrary/standard/LOMA6_001_svp.jpg',
                                                    style={'width': '100%'}
                                                ),
                                            ],
                                            type="dot",
                                        ),
                                        html.Div(id='table-characteristics-div', className='dcc_control'),
                                    ],
                                    id='plant-datatables',
                                    className='container-display',
                                ),
                        #     ],
                        # ),
                    ],
                    id='middle-column',
                    className='pretty_container three columns'                   
                ),

                html.Div(
                    [
                        dcc.Loading(
                            children=[dcc.Graph(id='plants-map')],
                            type="dot"
                        ),
                    ], 
                    id='right-column',
                    className='pretty_container four columns'
                ),
            ],
            className='row flex-display'
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"}
)

# Helper Functions
def filter_df_plants(selected_plant):
    df_plants_filtered = df_plants[df_plants['common_name']==selected_plant]
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

def filter_by_temperature(selected_df, selected_temp):
    return selected_df[selected_df['temperature_minimum_f'] >= selected_temp]

def filter_by_growth_habit(selected_df, growth_habit_list):
    for growth_habit in growth_habit_list:
        selected_df = selected_df[selected_df['growth_habit'].str.contains(growth_habit, case=False, na=False)]
    return selected_df

def transpose_classification(selected_df, selected_plant):
    df_transposed = selected_df
    plant_id = df_transposed[df_transposed['common_name'] == selected_plant]['id']
    df_transposed = df_transposed.drop('common_name', 1)
    df_transposed = df_transposed.set_index('id').transpose()
    df_transposed = df_transposed.reset_index()
    df_transposed = df_transposed[['index', int(plant_id)]]
    return df_transposed

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

# Zipcode dropdown updates temperature slider
@app.callback(
    Output('slider-temperature', 'value'),
    Input('zip-dropdown', 'value'),
    Input('slider-temperature', 'value')
)
def update_slider(zipcode, selected_temp):
    trigger_id = dash.callback_context.triggered[0]["prop_id"]
    if trigger_id == 'zip-dropdown.value':
        if zipcode is None:
            return dash.no_update
        zipcode_temp = df[df['zipcode']==zipcode]['min_temp'].item()
        if zipcode_temp <= selected_temp:
            return zipcode_temp
        # if zipcode_temp <= selected_temp:
        #     return df[df['zipcode']==zipcode]['min_temp'].item()
        # else:
        #     return -70
    return dash.no_update

# Update table using zip dropdown
@app.callback(
    Output('table-paging-and-sorting', 'data'),
    Input('zip-dropdown', 'value'),
    Input("checklist-duration", "value"),
    Input("checklist-image", "on"),
    Input("slider-temperature", "drag_value"),
    Input("dropdown-growth-habit", "value")
)   
def update_table(selected_zip, duration_list, image_selected_list, selected_temperature, growth_habit_list):
    data = df_plants
    # if selected_zip and duration_list and image_selected_list and growth_habit_list is None:  
    #     return data.to_dict('records')
    if selected_zip is not None:
        data = filter_by_zip(data, selected_zip)
    if duration_list is not None:
        data = filter_by_duration(data, duration_list)
    if image_selected_list:
        data = filter_by_image(data)   
    if selected_temperature > df_plants['temperature_minimum_f'].min():
        data = filter_by_temperature(data, selected_temperature)
    if growth_habit_list is not None:
        data = filter_by_growth_habit(data, growth_habit_list)
    return data.to_dict('records')

# Print temperature slider value
@app.callback(
    Output('slider-temperature-output', 'children'),
    Input('slider-temperature', 'drag_value')
)
def display_value(drag_value):
    # if drag_value < -65: zone = '0a'
    # elif -65 <= drag_value <= -60: zone = '0b'
    # elif -60 <= drag_value <= -55: zone = '1a'
    # elif -55 <= drag_value <= -50: zone = '1b'
    # elif -50 <= drag_value <= -45: zone = '2a'
    # elif -45 <= drag_value <= -40: zone = '2b'
    # elif -40 <= drag_value <= -35: zone = '3a'
    # elif -35 <= drag_value <= -30: zone = '3b'
    # elif -30 <= drag_value <= -25: zone = '4a'
    # elif -25 <= drag_value <= -20: zone = '4b'
    # elif -20 <= drag_value <= -15: zone = '5a'
    # elif -15 <= drag_value <= -10: zone = '5b'
    # elif -10 <= drag_value <= -5: zone = '6a'
    # elif -5 <= drag_value <= 0: zone = '6b'
    # elif 0 <= drag_value <= 5: zone = '7a'
    # elif 5 <= drag_value <= 10: zone = '7b'
    # elif 10 <= drag_value <= 15: zone = '8a'
    # elif 15 <= drag_value <= 20: zone = '8b'
    # elif 20 <= drag_value <= 25: zone = '9a'
    # elif 25 <= drag_value <= 30: zone = '9b'
    # elif 30 <= drag_value <= 35: zone = '10a'
    # elif 35 <= drag_value <= 40: zone = '10b'
    # elif 40 <= drag_value <= 45: zone = '11a'
    # elif 45 <= drag_value <= 50: zone = '11b'
    # elif 50 <= drag_value <= 55: zone = '12a'
    # elif 55 <= drag_value <= 60: zone = '12b'
    # elif 60 <= drag_value <= 65: zone = '13a'
    # else: zone = '13b'
    return 'Filter by Minimum Temperature: {}°F'.format(drag_value)

# Show image on datatable click
@app.callback(
    Output("image-url", "src"), 
    Input("table-paging-and-sorting", "active_cell"),
    prevent_initial_call=True
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
            return 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1200px-No-Image-Placeholder.svg.png'

# Update characteristics
@app.callback(
    Output('table-characteristics-div', 'children'),
    # Output("table-characteristics", "columns"),
    Input("common-dropdown", "value")
)
def update_table(selected_plant):
    if selected_plant is None:
        return dash.no_update
    df_characteristics = df_plants[['id', 'common_name', 'family_common_name', 'category', 'species']]
    data_characteristics = transpose_classification(df_characteristics, selected_plant)
    dict_chracteristics = data_characteristics.to_dict('records')

    df_growth = df_plants[['id', 'common_name', 'growth_habit', 'growth_rate', 'height_mature_feet', 'lifespan', 'toxicity']]
    data_growth = transpose_classification(df_growth, selected_plant)
    dict_growth = data_growth.to_dict('records')

    df_reproduction = df_plants[['id', 'common_name', 'bloom_period', 'fruit_seed_period_begin', 'fruit_seed_period_end', 'fruit_seed_abundance']]
    data_reproduction = transpose_classification(df_reproduction, selected_plant)
    dict_reproduction = data_reproduction.to_dict('records')

    return [
        html.Div(
            [
                dash_table.DataTable(
                    id='table-characteristics',
                    columns=[{'name': ['Characteristics', str(i)], 'id': str(i)} for i in data_characteristics.columns],
                    data=dict_chracteristics,
                    page_size=50,
                    style_table={'width': '50%'},
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)', 
                        'border': 'none', 
                        'textAlign': 'center'
                        },
                    style_header_conditional=[
                        {
                            'if': {'header_index': 1},
                            'display': 'none'
                        }
                    ],
                    style_cell={
                        'backgroundColor': colors['background'],
                        'color': colors['text'],
                        'textAlign': 'left',
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                        # 'border': 'none'
                    },
                    style_data_conditional=[                
                        {
                            'if': {'state': 'active'},  # 'active' | 'selected'
                            'backgroundColor': '#525F89',
                            'border': '#FFFFF'
                            # "border": "1px solid blue"                                    
                        },
                        {
                            'if': {'column_id': 'index'},
                            'textAlign': 'left'
                        }
                    ],
                    merge_duplicate_headers=True,
                    style_as_list_view=True,
                    css=[
                        {
                            'selector': 'tr:hover', 
                            'rule': 'background-color: #525F89;'
                        }
                    ],
                ),
            ],
            className='dcc_control'
        ),
        html.Div(
            [
                dash_table.DataTable(
                    id='table-growth',
                    columns=[{'name': ['Growth Requirements', str(i)], 'id': str(i)} for i in data_growth.columns],
                    data=dict_growth,
                    page_size=50,
                    style_table={'width': '50%'},
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)', 
                        'border': 'none', 
                        'textAlign': 'center'
                        },
                    style_header_conditional=[
                        {
                            'if': {'header_index': 1},
                            'display': 'none'
                        }
                    ],
                    style_cell={
                        'backgroundColor': colors['background'],
                        'color': colors['text'],
                        'textAlign': 'left',
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_data_conditional=[                
                        {
                            'if': {'state': 'active'},  # 'active' | 'selected'
                            'backgroundColor': '#525F89',
                            'border': '#FFFFF'
                            # "border": "1px solid blue"                                    
                        },
                        {
                            'if': {'column_id': 'index'},
                            'textAlign': 'left'
                        }
                    ],
                    merge_duplicate_headers=True,
                    style_as_list_view=True,
                    css=[
                        {
                            'selector': 'tr:hover', 
                            'rule': 'background-color: #525F89'
                        },
                    ],
                ),
            ],
            className='dcc_control'
        ),
        html.Div(
            [
                dash_table.DataTable(
                    id='table-reproduction',
                    columns=[{'name': ['Reproduction', str(i)], 'id': str(i)} for i in data_reproduction.columns],
                    data=dict_reproduction,
                    page_size=50,
                    style_table={'width': '50%'},
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)', 
                        'border': 'none', 
                        'textAlign': 'center'
                        },
                    style_header_conditional=[
                        {
                            'if': {'header_index': 1},
                            'display': 'none'
                        }
                    ],
                    style_cell={
                        'backgroundColor': colors['background'],
                        'color': colors['text'],
                        'textAlign': 'left',
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_data_conditional=[                
                        {
                            'if': {'state': 'active'},  # 'active' | 'selected'
                            'backgroundColor': '#525F89',
                            'border': '#FFFFF'
                            # "border": "1px solid blue"                                    
                        },
                        {
                            'if': {'column_id': 'index'},
                            'textAlign': 'left'
                        }
                    ],
                    merge_duplicate_headers=True,
                    style_as_list_view=True,
                    css=[
                        {
                            'selector': 'tr:hover', 
                            'rule': 'background-color: #525F89'
                        },
                    ],
                ),
            ],
            className='dcc_control'
        ),
    ]
        # table = dash_table.DataTable(
        #     id='table-paging-and-sorting',
        #     columns=[
        #         [{'name': i, 'id': i} for i in df_transposed]
        #     ],
        #     page_size=50,
        #     style_table={'height': '500px', 'overflowY': 'auto', 'marginTop': '15px'},
        #     style_header={'backgroundColor': '#525F89'},
        #     style_data_conditional=[                
        #         {
        #             'if': {'state': 'active'},  # 'active' | 'selected'
        #             'backgroundColor': '#525F89',
        #             'border': '#FFFFF'
        #             # "border": "1px solid blue"                                    
        #         },
        #         {
        #             'if': {'column_id': 'common_name'},
        #             'textAlign': 'center'
        #         }
        #     ],
        #     style_header_conditional=[
        #         {
        #             'if': {'column_id': 'common_name'},
        #             'textAlign': 'center'
        #         }
        #     ],
        #     style_cell={
        #         'backgroundColor': colors['background'],
        #         'color': colors['text'],
        #         'textAlign': 'left'
        #     },
        #     style_as_list_view=True,
        #     active_cell={'row': 3, 'column': 0, 'column_id': 'common_name', 'row_id': 36},
        #     css=[
        #         {
        #             'selector': 'tr:hover', 
        #             'rule': 'background-color: #525F89;'
        #         }
        #     ],
        # ),

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
    return selected_plant

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
        scientific = df_plants[df_plants['common_name'] == common]['scientific_name_x'].to_string(index=False)
        return [
            html.Label('Common Name'),
            dcc.Dropdown(
                id='common-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['common_name']],
                value=common,
                multi=False,
                className="dcc_control"
            ),
            html.Label('Scientific Name'),
            dcc.Dropdown(
                id='scientific-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['scientific_name_x']],
                value=scientific,
                multi=False,
                className="dcc_control"
            )
        ]
    if trigger_id == "scientific-dropdown.value":
        common = df_plants[df_plants['scientific_name_x'] == scientific]['common_name'].to_string(index=False)        
        return [
            html.Label(children='Common Name'),
            dcc.Dropdown(
                id='common-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['common_name']],
                value=common,
                multi=False,
                className="dcc_control"
            ),
            html.Label(children='Scientific Name'),
            dcc.Dropdown(
                id='scientific-dropdown',
                options=[{'label': i, 'value': i} for i in df_plants['scientific_name_x']],
                value=scientific,
                multi=False,
                className="dcc_control"
            )
        ]
    return dash.no_update

app.run_server(debug=True, use_reloader=False)