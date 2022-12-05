#!/usr/bin/env python
# coding: utf-8

# In[1]:


from functions import *
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_daq as daq
import dash_bootstrap_components as dbc


# In[2]:


#load and preprocess data
df = load_data('data', 'EU_flow_data_20220322.csv', wide_boolean=True, idx_boolean=False)

#dynamic sankey visualization with radio buttons and slider filters
app = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# In[ ]:


app.layout = html.Div([
    html.Div([
        html.Div(children=[
            html.Div(id='my-output')
        ], style={'margin': 'auto', 'text-align': 'center', 'fontFamily': 'Arial'}),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label('Change orientation:'),
                        dcc.RadioItems(
                            ['Vertical', 'Horizontal'],
                            value = 'Vertical',
                            id = 'orientation',
                            inline=True
                        )
                    ], style = {'text-align': 'center'}
                ),
                dbc.Col(
                    [
                        html.Label("Resource Unit:"),
                        dcc.RadioItems(
                            df['Value.type'].unique(),
                            value = df['Value.type'].unique()[0],
                            id='xaxis-column',
                            inline=True
                        )
                    ], style = {'text-align': 'center'}
                )
            ]
        )
    ], style={'height': '20%'}),
    html.Div([
        dcc.Graph(id='indicator-graphic', responsive=True) 
    ], style={'width': '100%', 'height': '70%'}),
    html.Div([
        dcc.Slider(
            df['Value.info'].min(),
            df['Value.info'].max(),
            step=None,
            id='year--slider',
            value=df['Value.info'].max(),
            marks={str(year): str(year) for year in df['Value.info'].unique()},
        )], style={'height': '10%', 'fontFamily': 'Arial', 'width': '70%', 'margin': 'auto'})

], style= {'height': '100vh'})

@app.callback(
    Output('indicator-graphic', 'figure'),
    Output('my-output', 'children'),
    Input('xaxis-column', 'value'),
    Input('year--slider', 'value'),
    Input('orientation', 'value')
)

def update_graph_and_title(xaxis_column_name, year_value, orientation_value):
    
    filter_list = [i and j for i, j in zip(df['Value.type'] == xaxis_column_name, df['Value.info'] == year_value)]
    temp_df = df[filter_list]
    
    #creating ordered lists of nodes' indices and their x-levels
    elements_positions, unique_sources_targets = calc_node_x(temp_df, 'Source', 'Target')

    #redeclare node_dict (this is done, because filtering the same node_dict will not work with Plotly as no breaks in numeric/integer node sequences can be handled. An alternative may be to manipulate the broken sequence, but manage to access the node_dict keys anyway)
    node_dict = dict()
    for i,e in zip(range(len(unique_sources_targets)), elements_positions):
        node_dict[str(unique_sources_targets[i])] = {'Source_level_str': e, 'Source_level_int': x_lvl_dict[e]["Int"], 'Node_index': i}

    #save each node's aggregated values in node_dict
    aggregate_node_values(temp_df, node_dict)
    #save each x-level's aggregated values in x_lvl_dict
    aggregate_values_by_x_level(node_dict, x_lvl_dict)

    payload_x, payload_y = nodes_xypositions(elements_positions, node_dict, x_lvl_dict)

    #sankey source and target payload for link dict
    source, target = calculate_link_sources_targets_alt(temp_df, node_dict)
    
    #define laylout level string
    keys_payload = x_level_strings(x_lvl_dict)
    
    payload_title = f"EU27 material flows in {year_value} for {xaxis_column_name} along {keys_payload}"
    
    #ready node data for mobile or larger displays
    node_config = dict(
        label = unique_sources_targets,
        x = [.001 if x==0 else .999 if x == 1 else x for x in payload_x],
        y = [.001 if y==0 else .999 if y == 1 else y for y in payload_y],
        pad = 20,
        thickness = 20,
        color = "cornsilk"
    )
    
    domain_config = dict(
        x =  [0,1],
        y =  [0,1]
    )
    
    orientation_payload = orientation_value[0].lower()
    
    if orientation_payload == 'v':
        
        node_config = dict(
            label = unique_sources_targets,
            pad = 20,
            thickness = 20,
            color = "cornsilk"
        )
        
    new_fig = go.Figure(data=[
        go.Sankey(
            orientation = orientation_payload,
            domain = domain_config,
            arrangement= "snap",
            node = node_config,
            link = dict(
                source = source,
                target = target,
                value = temp_df['Value']/1000,
                label = temp_df['Label'],
                color = temp_df['Colour']
            )
        )
    ])
    
    new_fig.update_layout(height = 600)
#     new_fig.layout.width = 1300 #0.9*user_gui_width 
#     new_fig.update_layout(height=700)

    return new_fig, payload_title

# Main
if __name__ == "__main__":
    app.run_server(debug=False)

