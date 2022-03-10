#!/usr/bin/env python
# coding: utf-8

# In[206]:


from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd


# In[207]:


app = Dash(__name__)


# In[208]:


def load_data(file_dir, file_name, idx_boolean = True, add_years = False):
    
    """
    Retrieve data, clean, manipulate and sort it.
    """
    
    file_path = f'{file_dir}/{file_name}'
    df = pd.read_csv(file_path)
    
    if idx_boolean:
        df.drop(df.columns[0], axis=1, inplace=True)
        
    if add_years:
        #copy data to test whether year slider works in plotly dash
        years_list_int = list(range(max(df['Value.info'].unique())+1,max(df['Value.info'].unique())+4))
        df_payload = df.iloc[:0].copy()

        for y in years_list_int:
            df_copy = df.copy()
            df_copy['Value.info'] = y
            df_payload = df_payload.append(df_copy)
            
        df = df.append(df_payload)
    
    df['Value'].replace("Inf", "0.0001")
    df['Value'] = df['Value'].astype("float")
    df['Value'].replace(0, 0.0001)
    
    return df


# In[209]:


#! essential, but problematic to set-up programatically, because of node level taxonomy

node_dict = {"Sourcing": 1, "Availability": 2, "Processing": 3, "Services": 4, "Outflows": 5}


# future data source: EU_flow_data_20220225.csv

# In[210]:


#! essential

df = load_data("data", "full_v3.csv", add_years= True)


# In[211]:


#! essential, but run once only and take care when using further and other colors!!!
colors = list(df['Colour'].unique())
color_codes = ['#363737', '#caff70', '#00bfff', '#eeb422', '#2f4f4f']
color_dict = dict(zip(colors, color_codes))

def convert_colors(df, color_column, color_dict):
    '''
    Convert color signatures to actionable data.
    '''
    color_payload = []    
    
    for j in range(0, len(df)):
        for color, code in color_dict.items():
            if color == df[color_column].values[j]:
                color_payload.append(code);
                break;
    return color_payload;


# In[212]:


#! essential: add actionable color palette to df

colors_df = pd.DataFrame(index=range(len(df)),columns=range(1))
colors_df.columns = ["hex_colors"]
df = df.join(colors_df)
df['hex_colors'] = convert_colors(df, 'Colour', color_dict)


# In[213]:


#! since code was repetitive with unique_sources_targets, the function returns a list of 2 lists now

def calc_node_x(df, source_column, target_column):
    '''
    Calculate the x-position of Source and Target elements, and save it in a list.
    
    Important potentially data- and visualization-driven manipulations:
    
    1: The setup is designed so that node_levels are not equal, i.e. df$Target elements not found 
    in df$Source, cannot be assigned the df$Source.level, but must be looked at df$Target.level instead.
    
    Nota bene on plotly: Apparently no distinction btw. 0 and .1 on the x-axis.
    
    Questions:
    Role of source 2 target relation and how it should be handled
    Role of Source.level 2 Target.level relation and how it should be handled
    
    '''
    
    x_payload = []
    sources_targets = []

    sources = list(df[source_column].unique())
    targets = list(df[target_column].unique())
    sources_targets.extend(sources)
    sources_targets.extend(set(targets) - set(sources))
        
    i = 0
    while i < len(sources_targets):
        while i < len(sources):
            temp_df = df.loc[df[source_column] == sources_targets[i]]
            source_target = temp_df.iloc[0,0]
            x_payload.append(source_target)
            i += 1
        else:
            temp_df = df.loc[df[target_column] == sources_targets[i]]
            source_target = temp_df.iloc[0,1]
            x_payload.append(source_target)
            i += 1
        
    unordered_sl_payload = []
    
    for load in x_payload:
        for node, level in node_dict.items():
            if load == node:
                unordered_sl_payload.append(level)
                break;
    
    list1 = unordered_sl_payload
    list2 = sources_targets
    
    
    zipped_lists = zip(list1, list2)
    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)

    list1, list2 = [ list(tuple) for tuple in  tuples]
    
    export_list = []
    
    for l in list1:
        for node, level in node_dict.items():
            if level == l:
                export_list.append(node)
                break;
    
    return [export_list, list2];


# In[214]:


elements_positions, unique_sources_targets = calc_node_x(df, 'Source', 'Target')


# In[215]:


#calculate sources_targets y size

def sources_targets_y_frequency(elements_positions, node_dict):
    
    sources_targets_on_x = []

    for key, value in node_dict.items():
        sources_targets_on_x.append(elements_positions.count(key))

    sources_targets_y_size = []

    for i in sources_targets_on_x:
        batch = []
        for j in range(1, i+1):
            batch.append(j/i)
        sources_targets_y_size.append(batch)
    
    
    
    return [round(item,2) for sublist in sources_targets_y_size for item in sublist]

sources_targets_y_size = sources_targets_y_frequency(elements_positions, node_dict)


# In[216]:


#calculate sources_targets x position

def sources_targets_x_frequency(elements_positions, node_dict):
    '''
    interestingly, subtracting .2 from below items, will produce float values close to ints
    '''

    sources_targets_on_y = []

    for i in elements_positions:
        for key, value in node_dict.items():
            if i == key:
                sources_targets_on_y.append(value/len(node_dict))
                
    return sources_targets_on_y
                
sources_targets_on_y = sources_targets_x_frequency(elements_positions, node_dict)


# In[217]:


#calculate link sources and targets

def calculate_link_sources_targets(df, unique_sources_targets):
    
    links_sources = []
    for i in range(len(df)):
        for j in range(len(unique_sources_targets)):
            if df.iloc[i,2] == unique_sources_targets[j]:
                links_sources.append(j)
                break;

    #calculate link 
    links_targets = []
    for i in range(len(df)):
        for j in range(len(unique_sources_targets)):
            if df.iloc[i,3] == unique_sources_targets[j]:
                links_targets.append(j)
                break;

    return [links_sources, links_targets]

links_sources_targets = calculate_link_sources_targets(df, unique_sources_targets)


# #! essential
# #plotly sankey architecture with df or df_temp application guess
# fig = go.Figure(data=[go.Sankey(
#     #template = 'plotly_white',
#     arrangement= "freeform",
#     node = dict(
#       label = unique_sources_targets, #df
#       x = [.001 if x==0.2 else round(x - 0.2,1) for x in sources_targets_on_y], #df_temp
#       y = [.999 if y==1 else y for y in sources_targets_y_size], #df_temp
#       pad = 8,
#       thickness = 5,
#       color = "cornsilk"
#     ),
#     link = dict(
#       source = links_sources_targets[0], #df_temp
#       target = links_sources_targets[1], #df_temp
#       value = df['Value']/1000, #df
#       label = df['Label'], #df
#       color = df['hex_colors'] #df
#   ))])
# 
# # fig.update_layout(title_text="EU28 material flows in 2017 Mass_now/kt Source | Availability | Processing | Services/goods | Outflows", font_size=10)
# fig.update_layout(width = 10*1920/10, height = 7*1080/10, title_text="EU28 material flows in 2017 Mass_now/kt Source | Availability | Processing | Services/goods | Outflows", font_size=10)
# #fig.update_layout(grid_domain_x = list([1,1]), grid_domain_y = list([0,1]))
# #fig.update_traces(aaxis_showgrid=True)
# #fig.update_xaxes(showline=True, linewidth=1, gridcolor='LightPink')
# #fig.update_yaxes(showline=True, linewidth=1, gridcolor='LightPink')
# fig.show()

# with radio buttons

# In[218]:


app.layout = html.Div([
    html.Div([
        html.Div(children=[
            html.Div(id='my-output')
        ], style={'margin': 'auto', 'text-align': 'center', 'fontFamily': 'Arial'}),
        html.Br(),
        html.Br(),
        html.Div([
            dcc.RadioItems(
                df['Value.type'].unique(),
                'Energy_now',
                id='xaxis-column',
                inline=True
            )], style={'fontFamily': 'Arial', 'width': '48%', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    html.Div([
        dcc.Slider(
            df['Value.info'].min(),
            df['Value.info'].max(),
            step=None,
            id='year--slider',
            value=df['Value.info'].max(),
            marks={str(year): str(year) for year in df['Value.info'].unique()},
        )], style={'fontFamily': 'Arial'})
    
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    Output('my-output', 'children'),
    Input('xaxis-column', 'value'),
    Input('year--slider', 'value'))
def update_graph_and_title(xaxis_column_name, year_value):
    
    filter_list = [i and j for i, j in zip(df['Value.type'] == xaxis_column_name, df['Value.info'] == year_value)]
    temp_df = df[filter_list]

    payload = f"EU28 material flows in {year_value} for {xaxis_column_name} along Source | Availability | Processing | Services/goods | Outflows"

    #add logic to calculate new node x,y & link source, target
    new_elements_positions, new_unique_sources_targets = calc_node_x(temp_df, 'Source', 'Target')
    new_sources_targets_y_size = sources_targets_y_frequency(new_elements_positions, node_dict)
    new_sources_targets_on_y = sources_targets_x_frequency(new_elements_positions, node_dict)
    new_links_sources_targets = calculate_link_sources_targets(temp_df, new_unique_sources_targets)

    new_fig = go.Figure(data=[go.Sankey(
        domain = dict(
          x =  [0,1],
          y =  [0,1]
        ),
        node = dict(
          label = new_unique_sources_targets,
          x = [.001 if x==0.2 else round(x - 0.2,1) for x in new_sources_targets_on_y],
          y = [0.99 if y == 1 else y for y in new_sources_targets_y_size],
    #      pad = 5,
          thickness = 5,
          color = "cornsilk"
        ),
        link = dict(
          source = new_links_sources_targets[0],
          target = new_links_sources_targets[1],
          value = temp_df['Value']/1000,
          label = temp_df['Label'],
          color = temp_df['hex_colors']
      ))])
    
    new_fig.update_layout(height=750)

    return new_fig, payload
if __name__ == '__main__':
    app.run_server(port = 8051, debug=True)


# In[ ]:




