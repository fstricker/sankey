#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import re

def load_data(file_dir, file_name, wide_boolean = True, idx_boolean = False, add_years = False):
    
    """
    Retrieve data, clean, manipulate and sort it.
    """
    
    file_path = f'{file_dir}/{file_name}'
    df = pd.read_csv(file_path)
    
    if wide_boolean:
        #reorder
        new_order = [2,3,0,1]
        new_order.extend(list(range(4, len(df.columns))))
        new_df = df[df.columns[new_order]]
        new_df.rename(columns = {'Unit':'Value.type'}, inplace = True)


        #find number of year columns
        expr = "X\d+"
        year_cols = []
        for c in new_df.columns:
            if re.findall(expr, str(c)):
                year_cols.append(c)

        #create final df structure
        df_labels = new_df.iloc[:0].copy()
        df_base = df_labels[df_labels.columns[list(range(len(df_labels.columns)-len(year_cols)))]]
        df_ext = pd.DataFrame(columns = ["Value.info", "Value"])
        new_df = df_base.join(df_ext)

        #set target df column order
        new_df_order = [2,3,0,1]
        new_df_order.extend(list(range(4, len(new_df.columns))))

        #row wise population of new_df
        for i in range(len(df)):

            #split df row in base data and repeat it
            inc_data = df.iloc[[i], list(range(len(df.columns)-len(year_cols)))]
            inc_data = pd.concat([inc_data]*len(year_cols), ignore_index=True)

            #split df row in to-be-transposed data
            inc_ext = df.iloc[[i], list(range(len(df.columns)-len(year_cols), len(df.columns)))]
            inc_ext = inc_ext.transpose()
            inc_ext_data = {'Value.info': list(inc_ext.index.values),
                            'Value': list(inc_ext[i].values)
                           }
            #combine data in new df structure
            inc_df = pd.DataFrame(inc_ext_data, columns = ['Value.info','Value'], index = list(range(len(inc_ext))))
            inc_df = inc_data.join(inc_df)
            inc_df = inc_df[inc_df.columns[new_df_order]]
            inc_df.rename(columns = {'Unit':'Value.type'}, inplace = True) 

            #append data to new df
            new_df = new_df.append(inc_df, ignore_index = True)
        
        #slice string of col_years and convert it to int
        new_df['Value.info'] = new_df['Value.info'].str.slice(1)
        new_df['Value.info'] = new_df['Value.info'].astype(int)
        
        #replace ","" with "."" in Value col, and overwrite df
        new_df['Value'] = new_df['Value'].astype("str")
        new_df['Value'] = new_df['Value'].str.replace(",", ".")
        df = new_df
    
    
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
    
    df = df.dropna()
    df['Value'].replace("Inf", "0.0001")
    df['Value'] = df['Value'].astype("float")
    df['Value'].replace(0, 0.0001)

    #aggregate data by all cols over Value
    df_cols_excl_value = list(df.columns[0:len(df.columns)-1])
    df = df.groupby(df_cols_excl_value).agg({'Value': ['sum']}).reset_index()
    df_cols_excl_value.extend(['Value'])
    df.columns = df_cols_excl_value
    
    return df

#! essential, but problematic to set-up programatically, because of node level taxonomy

x_lvl_dict = {"Sourcing": {"Int": 1}, "Availability": {"Int": 2}, "Processing": {"Int": 3}, "Services": {"Int": 4}, "Outflows": {"Int": 5}}

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
        for node, level in x_lvl_dict.items():
            if load == node:
                unordered_sl_payload.append(level['Int'])
                break;
    
    list1 = unordered_sl_payload
    list2 = sources_targets
    
    
    zipped_lists = zip(list1, list2)
    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)

    list1, list2 = [ list(tuple) for tuple in  tuples]
    
    export_list = []
    
    for l in list1:
        for node, level in x_lvl_dict.items():
            if level['Int'] == l:
                export_list.append(node)
                break;
    
    return [export_list, list2];

#calculate sources_targets y size

def sources_targets_y_frequency(elements_positions, x_lvl_dict):
    
    sources_targets_on_x = []

    for key, value in x_lvl_dict.items():
        sources_targets_on_x.append(elements_positions.count(key))

    sources_targets_y_size = []

    for i in sources_targets_on_x:
        batch = []
        for j in range(1, i+1):
            batch.append(j/i)
        sources_targets_y_size.append(batch)
    
    
    
    return [round(item,2) for sublist in sources_targets_y_size for item in sublist]

#calculate sources_targets x position

def sources_targets_x_frequency(elements_positions, x_lvl_dict):
    '''
    interestingly, subtracting .2 from below items, will produce float values close to ints
    '''

    sources_targets_on_y = []

    for i in elements_positions:
        for key, value in x_lvl_dict.items():
            if i == key:
                sources_targets_on_y.append(value["Int"]/len(x_lvl_dict))
                
    return sources_targets_on_y

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

#alternate shorter calculation of link sources and targets

def calculate_link_sources_targets_alt(df, node_dict):
    
    links_sources = []
    links_targets = []
    
    for i in range(len(df)):
        links_sources.append(node_dict[df.iloc[i,2]]['Node_index'])
        links_targets.append(node_dict[df.iloc[i,3]]['Node_index'])

    return [links_sources, links_targets]

#alternate shorter calculation of link sources and targets

def calculate_link_sources_targets_alt(df, node_dict):
    
    links_sources = []
    links_targets = []
    
    for i in range(len(df)):
        links_sources.append(node_dict[df.iloc[i,2]]['Node_index'])
        links_targets.append(node_dict[df.iloc[i,3]]['Node_index'])

    return [links_sources, links_targets]

def aggregate_node_values(df, node_dict):

    col_payload_source_agg = ['Source']
    col_payload_target_agg = ['Target']

    df_source_agg = df.groupby(col_payload_source_agg).agg({'Value': ['sum']}).reset_index()
    df_target_agg = df.groupby(col_payload_target_agg).agg({'Value': ['sum']}).reset_index()

    col_payload_source_agg.append('Value.Source')
    col_payload_target_agg.append('Value.Target')

    df_source_agg.columns = col_payload_source_agg
    df_target_agg.columns = col_payload_target_agg

    df_source_agg = df_source_agg.set_index('Source')
    df_target_agg = df_target_agg.set_index('Target')

    df_agg = df_target_agg.join(df_source_agg, how = 'outer')

    #add max to node_dict dictionary
    for key in df_agg.index:
        if pd.isna(df_agg.loc[key][0]):
            node_dict[key]['Max_value'] = df_agg.loc[key][1]
        else:
            node_dict[key]['Max_value'] = max(df_agg.loc[key])

def aggregate_values_by_x_level(node_dict, x_lvl_dict):    
    #find max aggregated value of x-level (nodes' max value between sum of source flows, and sum of target flows)
    
    for key, value in x_lvl_dict.items():
        
        value_payload = 0
        
        for node, content in node_dict.items():
            if key == content['Source_level_str']:
                value_payload += content['Max_value']
        
        x_lvl_dict[key]['Agg_Value'] = value_payload
        
def nodes_xypositions(elements_positions, node_dict, x_lvl_dict):
    
    #type=list, what=nodes' x-positions
    payload_x = []
    
    #type=list, what=count of nodes by x_lvl
    sources_targets_on_x = []
    
    #type=list, what=list of nodes' y-positions by x_lvl
    sources_targets_y_size = []

    for key, value in x_lvl_dict.items():
        sources_targets_on_x.append(elements_positions.count(key))
        
        y_sum = 0
        
        for node, item in node_dict.items():
                        
            if item['Source_level_str'] == key:
                
                #add x position
                payload_x.append(item['Source_level_int']/len(x_lvl_dict))
                
                #add y position
                sources_targets_y_size.append((item['Max_value'] + y_sum)/value['Agg_Value'])
                
                y_sum += item['Max_value']
                
    return [payload_x, sources_targets_y_size]