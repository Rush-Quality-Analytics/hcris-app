import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
#import dash_bootstrap_components as dbc
#from dash.exceptions import PreventUpdate

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import warnings
#import sys
import re
import csv
    
#from urllib.request import urlopen
#import urllib
#from math import isnan
import numpy as np
import statsmodels.api as sm
from scipy import stats

#warnings.filterwarnings('ignore')
#pd.set_option('display.max_columns', None)


px.set_mapbox_access_token('pk.eyJ1Ijoia2xvY2V5IiwiYSI6ImNrYm9uaWhoYjI0ZDcycW56ZWExODRmYzcifQ.Mb27BYst186G4r5fjju6Pw')
################################# CONFIG APP #################################


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.config.suppress_callback_exceptions = True


################################# LOAD DATA ##################################


gendat_df = pd.read_pickle('dataframe_data/GenDat4App.pkl')
 
gendat_df[('Hospital type, text', 'Hospital type, text', 'Hospital type, text', 'Hospital type, text')] = gendat_df[('Hospital type, text', 'Hospital type, text', 'Hospital type, text', 'Hospital type, text')].replace(np.nan, 'NaN')
gendat_df[('Control type, text', 'Control type, text', 'Control type, text', 'Control type, text')] = gendat_df[('Control type, text', 'Control type, text', 'Control type, text', 'Control type, text')].replace(np.nan, 'NaN')


######################## SELECTION LISTS #####################################


HOSPITALS = gendat_df[('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')].tolist()
beds = gendat_df[('S3_1_C2_27', 'Total Facility', 'NUMBER OF BEDS', 'Total Facility (S3_1_C2_27)')].tolist()
states = gendat_df[('S2_1_C2_2', 'Hospital State', '', 'Hospital State (S2_1_C2_2)')].tolist()
htypes = gendat_df[('Hospital type, text', 'Hospital type, text', 'Hospital type, text', 'Hospital type, text')].tolist()
ctypes = gendat_df[('Control type, text', 'Control type, text', 'Control type, text', 'Control type, text')].tolist()

htypes = ['NaN' if x is np.nan else x for x in htypes]
ctypes = ['NaN' if x is np.nan else x for x in ctypes]

HOSPITALS, beds, states, htypes, ctypes = (list(t) for t in zip(*sorted(zip(HOSPITALS, beds, states, htypes, ctypes))))
HOSPITALS_SET = sorted(list(set(HOSPITALS)))


with open('dataframe_data/report_categories.csv', newline='') as csvfile:
    categories = csv.reader(csvfile, delimiter=',')
    for row in categories:
        report_categories = row
report_categories.sort()

with open('dataframe_data/sub_categories.csv', newline='') as csvfile:
    categories = csv.reader(csvfile, delimiter=',')
    for row in categories:
        sub_categories = row
sub_categories.sort()

url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/1125SIRFRANCISDRAKEOPERATINGCO(052043).csv'

main_df = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
main_df = pd.DataFrame(columns = main_df.columns)


################# DASH APP CONTROL FUNCTIONS #################################

def obs_pred_rsquare(obs, pred):
    return 1 - sum((obs - pred) ** 2) / sum((obs - np.mean(obs)) ** 2)


def description_card1():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card1",
        children=[
            html.H5("Healthcare cost reports", style={
            'textAlign': 'left',
        }),
           dcc.Markdown(" Until now, using data from the Healthcare Cost Report Information System (HCRIS) meant tackling large complicated files with expensive software, or paying someone else to do it. This app allows you to analyze and download 2,000+ cost related variables for 9,000+ hospitals.",
                  ),
            html.Br(),
            dcc.Markdown("This app runs on free servers, not super computers. If you want to analyze hundreds of hospitals at once, you can run the app locally by downloading the [source code](https://github.com/Rush-Quality-Analytics/hcris-app). Maybe you just want the [curated data](https://github.com/Rush-Quality-Analytics/HCRIS-databuilder).",
            ),
        ],
    )

def description_card2():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card2",
        children=[
            html.H5("Healthcare cost reports", style={
            'textAlign': 'left',
        }),
           html.P("Use this tab to analyze cost report data for an individual hospital." +
                  " Most hospitals will not have data for most variables. Use the top left plot" +
                  " to see which variables your chosen hospital has data for." +
                  " Use the top right plot to examine one variable against another; choose from" +
                  " 4 statistical fits.",
                  style={
            'textAlign': 'left',
        }), 
        ],
    )



def generate_control_card1():
    
    """
    :return: A Div containing controls for graphs.
    """
    
    return html.Div(
        id="control-card1",
        children=[
            
            html.Br(),
            html.H5("Filter on the options below"),
            
            html.Div(id='Filterbeds1'),
            dcc.RangeSlider(
                id='beds1',
                count=1,
                min=1,
                max=2752,
                step=1,
                
                value=[1, 2752],
                ),
            
            html.Br(),
            html.P("Select hospital types"),
            dcc.Dropdown(
                id="hospital_type1",
                options=[{"label": i, "value": i} for i in list(set(htypes))],
                multi=True,
                value=list(set(htypes)),
                style={
                    #'width': '320px', 
                    'font-size': "100%",
                    },
                ),
            
            html.Br(),
            html.P("Select hospital control types"),
            dcc.Dropdown(
                id="control_type1",
                options=[{"label": i, "value": i} for i in list(set(ctypes))],
                multi=True,
                value=list(set(ctypes)),
                style={
                    #'width': '320px', 
                    'font-size': "100%",
                    },
                ),
            
            html.Br(),
            html.P("Select a set of states"),
            dcc.Dropdown(
                id="states-select1",
                options=[{"label": i, "value": i} for i in list(set(states))],
                multi=True,
                value=list(set(states)),
                style={
                    #'width': '320px', 
                    'font-size': "100%",
                    }
            ),
            html.Br(),
            
            html.P("Select a set of hospitals to compare. Scroll or start typing keywords."),
            dcc.Dropdown(
                id="hospital-select1",
                options=[{"label": i, "value": i} for i in HOSPITALS_SET],
                multi=True,
                value=None,
                optionHeight=50,
                style={
                    #'width': '320px',
                    'font-size': "90%",
                    }
            ),
            html.Br(),
            
            html.P("Select a report category to analyze. Scroll or start typing keywords. Once a category is chosen, the app will automatically filter on the sub-categories that contain data for at least one of your chosen hospitals."),
            dcc.Dropdown(
                id="categories-select1",
                options=[{"label": i, "value": i} for i in report_categories],
                value=None,
                optionHeight=70,
                style={
                    #'width': '320px', 
                    'font-size': "90%",
                    }
            ),
            html.Br(),

            dcc.RadioItems(
                id='categories-select11',
                style={
                    #'width': '320px', 
                    'font-size': "90%",
                    }
            ),
        ],
    )



def generate_control_card2():
    
    """
    :return: A Div containing controls for graphs.
    """
    
    return html.Div(
        id="control-card2",
        children=[
            
            html.H5("Select a hospital"),
            dcc.Dropdown(
                id="focal-hospital-select2",
                options=[{"label": i, "value": i} for i in HOSPITALS_SET],
                multi=False,
                value=None,
                optionHeight=50,
                style={
                    'width': '300px',
                    'font-size': "90%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    'padding': '0px',
                    'margin-top': '0px',
                    }
                ),
            
        ],
        style={
                    #'width': '2000px', 
                    'font-size': "90%",
                    'display': 'inline-block',
                    },
    )





def generate_control_card3():
    
    """
    :return: A Div containing controls for graphs.
    """
    
    return html.Div(
        id="control-card3",
        children=[
            
            html.H5("Examine relationships between variables"),
            html.P("Select a category and sub-category for your x-variable. Scroll or start typing keywords"),
            dcc.Dropdown(
                id="categories-select2",
                options=[{"label": i, "value": i} for i in report_categories],
                value=None,
                optionHeight=70,
                style={
                    'width': '250px', 
                    'font-size': "90%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    #'box-shadow': '1px 1px 1px grey',
                    #'background-color': '#f0f0f0',
                    'padding': '0px',
                    'margin-bottom': '0px',
                    }
            ),
            dcc.Dropdown(
                id="categories-select22",
                options=[{"label": i, "value": i} for i in report_categories],
                value=None,
                optionHeight=70,
                style={
                    'width': '250px', 
                    'font-size': "90%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    #'box-shadow': '1px 1px 1px grey',
                    #'background-color': '#f0f0f0',
                    'padding': '0px',
                    'margin-left': '10px',
                    }
            ),
            
            
            html.P("Select a category and sub-category for your y-variable. Scroll or start typing keywords"),
            dcc.Dropdown(
                id="categories-select2-2",
                options=[{"label": i, "value": i} for i in report_categories],
                value=None,
                optionHeight=70,
                style={
                    'width': '250px', 
                    'font-size': "90%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    #'box-shadow': '1px 1px 1px grey',
                    #'background-color': '#f0f0f0',
                    'padding': '0px',
                    'margin-bottom': '0px',
                    }
            ),
            dcc.Dropdown(
                id="categories-select22-2",
                options=[{"label": i, "value": i} for i in report_categories],
                value=None,
                optionHeight=70,
                style={
                    'width': '250px', 
                    'font-size': "90%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    #'box-shadow': '1px 1px 1px grey',
                    #'background-color': '#f0f0f0',
                    'padding': '0px',
                    'margin-left': '10px',
                    }
            ),
            
        ],
        style={
            #'width': '2000px', 
            'font-size': "90%",
            'display': 'inline-block',
            },
    )




def generate_control_card4():
    
    """
    :return: A Div containing controls for graphs.
    """
    
    return html.Div(
        id="control-card4",
        children=[
            
            html.P("Select a model for fitting a trendline"),
            dcc.Dropdown(
                id='trendline-1',
                value='locally weighted',
                style={
                    'width': '200px', 
                    'font-size': "100%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    #'box-shadow': '1px 1px 1px grey',
                    #'background-color': '#f0f0f0',
                    'padding': '0px',
                    'margin-left': '0px',
                    }
            ),
            
        ],
        style={
            #'width': '2000px', 
            'font-size': "90%",
            'display': 'inline-block',
            },
    )




def generate_control_card5():
    
    """
    :return: A Div containing controls for graphs.
    """
    
    return html.Div(
        id="control-card5",
        children=[
            
            html.H5("Breakdown financial reports by category"),
            html.P("Select a category. Scroll or start typing keywords."),
            dcc.Dropdown(
                id="categories-select2-3",
                options=[{"label": i, "value": i} for i in report_categories],
                value=None,
                optionHeight=70,
                style={
                    'width': '250px', 
                    'font-size': "90%",
                    'display': 'inline-block',
                    'border-radius': '15px',
                    #'box-shadow': '1px 1px 1px grey',
                    #'background-color': '#f0f0f0',
                    'padding': '0px',
                    'margin-bottom': '0px',
                    }
            ),
            
        ],
        style={
            #'width': '2000px', 
            'font-size': "90%",
            'display': 'inline-block',
            },
    )



#########################################################################################
################### DASH APP PLOT FUNCTIONS #############################################
#########################################################################################    













  
    
    
########################### DASH APP LAYOUT ##################################


app.layout = html.Div([
    
    dcc.Store(id='df_tab1', storage_type='memory'),
    dcc.Store(id='df_tab2', storage_type='memory'),
    
    dcc.Tabs([
        
        dcc.Tab(label='Cost Reports Across Hospitals',
        children=[
        
        # Banner
        html.Div(
            style={'background-color': '#f9f9f9'},
            id="banner1",
            className="banner",
            children=[  html.Img(src=app.get_asset_url("RUSH_full_color.jpg"),
                               style={'textAlign': 'left'}),
                        html.Img(src=app.get_asset_url("plotly_logo.png"),
                               style={'textAlign': 'right'}),
                      ],
        ),
        # Left column
        html.Div(
            id="left-column1",
            className="three columns",
            children=[description_card1(), generate_control_card1()],
            style={'width': '24%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
            },
        ),
        # Right column
        html.Div(
            id="right-column1",
            className="eight columns",
            children=[
                
                html.Div(
                    id="map1",
                    children=[
                        html.B("Map of selected hospitals"),
                        html.Hr(),
                        dcc.Graph(id="map_plot1"),
                    ],
                    style={'width': '100%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
                                 #'fontSize':16
                            },
                ),
                
                html.Div(
                    [html.B(str(len(HOSPITALS_SET)) + " hospitals available", style={'fontSize':16}),
                     html.H6(id="text1", style={'fontSize':16},)],
                    id="des1",
                    className="mini_container",
                    style={
                        'width': '35%',
                        'display': 'inline-block',
                        #'border-radius': '0px',
                        #'box-shadow': '1px 1px 1px grey',
                        #'background-color': '#f0f0f0',
                        #'padding': '0px',
                        #'margin-right': '0px',
                        #'margin-bottom': '10px',
                        'fontSize':16,
                        'textAlign': 'center',
                        },
                    ),
                    
                html.Div(
                    [html.B('Download the full cost reports for the selected hospitals', style={'fontSize':16}),
                     html.Br(),
                     html.A('Cost_Reports_Full.csv',
                            id="data_link", download="Cost_Reports_Full.csv",
                        href="",
                        target="_blank",
                        style={'fontSize':16}
                        ),
                     html.Br(),
                        ],
                    id="des3",
                    className="mini_container",
                    style={
                        'width': '62%',
                        'display': 'inline-block',
                        #'border-radius': '0px',
                        #'box-shadow': '1px 1px 1px grey',
                        #'background-color': '#f0f0f0',
                        #'padding': '0px',
                        #'margin-right': '0px',
                        #'margin-bottom': '10px',
                        'fontSize':16,
                        'textAlign': 'center',
                        },
                    ),
                
                #html.Br(),
                #html.Br(),
                html.Div(
                    id="cost_report1",
                    children=[
                        html.B("Cost Report Across Fiscal Years"),
                        html.Hr(),
                        dcc.Graph(id="cost_report_plot1"),
                    ],
                    style={'width': '100%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
                                 #'fontSize':16
                            },
                ),
                html.Br(),
                html.Br(),
                
                
                html.Div(
                    id="table_report1",
                    children=[
                        html.B("Cost Report Across Fiscal Years"),
                        html.Hr(),
                        dcc.Graph(id="table1"),
                    ],
                    style={'width': '100%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
                                 #'fontSize':16
                            },
                ),
                html.Br(),
                html.Br(),
                
                
                html.Div(
                    id="cost_report2",
                    children=[
                        html.B("Hospital Rankings for Cost Report Across Fiscal Years"),
                        html.Hr(),
                        dcc.Graph(id="cost_report_plot2"),
                    ],
                    style={'width': '100%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
                                 #'fontSize':16
                            },
                ),
            ],
        ),
        ],
        ),
        
        dcc.Tab(label='Single Hospital Analysis',
        children=[
        
        # Banner
        html.Div(
            style={'background-color': '#f9f9f9'},
            id="banner2",
            className="banner",
            children=[  html.Img(src=app.get_asset_url("RUSH_full_color.jpg"),
                               style={'textAlign': 'left'}),
                        html.Img(src=app.get_asset_url("plotly_logo.png"),
                               style={'textAlign': 'right'}),
                      ],
        ),
        html.Div(
            id="left-column2",
            className="columns",
            children=[description_card2(), generate_control_card2()],
            style={'width': '95%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
            },
        ),
        
        html.Div(
        id="right-column3",
        className="five columns",
        children=[
            
            html.Div(
                id="single_hospital_cost_report_plot4",
                children=[
                    generate_control_card5(),
                    dcc.Graph(id="cost_report_plot4"),
                ],
                style={
                        'width': '110%',
                        #'display': 'inline-block',
                        'border-radius': '15px',
                        'box-shadow': '1px 1px 1px grey',
                        'background-color': '#f0f0f0',
                        'padding': '10px',
                        'margin-bottom': '10px',
                        #'margin-right': '0px',
                        'height': '770px',
                        #'fontSize':16
                        },
                ),
            ],
        ),
        
        html.Div(
            id="right-column2",
            className="six columns",
            children=[
                html.Div(
                    id="single_hospital_cost_report_plot3",
                    children=[
                        generate_control_card3(),
                        dcc.Graph(id="cost_report_plot3"),
                        generate_control_card4(),
                    ],
                    style={
                            'width': '100%',
                            #'display': 'inline-block',
                            'border-radius': '15px',
                            'box-shadow': '1px 1px 1px grey',
                            'background-color': '#f0f0f0',
                            'padding': '10px',
                            'margin-left': '60px',
                            'margin-bottom': '10px',
                            'height': '770px',
                            #'fontSize':16
                            },
                    ),
                ],                
            ),
        ],
        ),
        
        
    ],),
],)



    
###############################    TAB 1    #############################################
#########################################################################################
@app.callback( # Updated number of beds text
    Output('Filterbeds1', 'children'),
    [
     Input('beds1', 'value'),
     ],
    #prevent_initial_call=True,
    )
def update_output1(value):
    return 'Filter on number of beds: {}'.format(value)



@app.callback( # Updated number of beds text
    Output('Filterbeds2', 'children'),
    [
     Input('beds2', 'value'),
     ],
    #prevent_initial_call=True,
    )
def update_output6(value):
    return 'Filter on number of beds: {}'.format(value)


@app.callback( # Update available sub_categories
    Output('categories-select11', 'options'),
    [
     Input('categories-select1', 'value'),
     Input('df_tab1', "data"),
     ],
    #prevent_initial_call=True,
    )
def update_output3(value, df):
    main_df2 = main_df.iloc[:, (main_df.columns.get_level_values(2)==value)]
    sub_cat = main_df2.columns.get_level_values(3).tolist()
    del main_df2
    
    if df is not None:
        df = pd.read_json(df)
        df.dropna(axis=1, thresh = int(np.round(0.5*df.shape[0],0)), inplace=True) # 
        cols1 = list(df)
        cols2 = []
        for c in cols1:
            s = c.split("', ")[-1]
            s = s[1:-2]
            cols2.append(s)
            
        sub_categories = []
        for c in sub_cat:
            if c in cols2:
                sub_categories.append(c)
    else:
        sub_categories = sub_cat
        
    return [{"label": i, "value": i} for i in sub_categories]



@app.callback( # Select sub-category
    Output('categories-select11', 'value'),
    [
     Input('categories-select11', 'options'),
     ],
    #prevent_initial_call=True,
    )
def update_output4(available_options):
    try:
        return available_options[0]['value']
    except:
        return 'NUMBER OF BEDS'
    
    
@app.callback(
    Output('hospital-select1', 'options'),
    [
     Input('beds1', 'value'),
     Input('states-select1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     ],
    #prevent_initial_call=True,
    )
def update_hospitals(bed_range, states_vals, htype_vals, ctype_vals):
    
    low, high = bed_range
    hospitals = []
    for i, h in enumerate(HOSPITALS):
        b = beds[i]
        s = states[i]
        ht = htypes[i]
        ct = ctypes[i]
        if b > low and b < high:
            if s in states_vals:
                if ht in htype_vals:
                    if ct in ctype_vals:
                        hospitals.append(h)
            
    hospitals = list(set(hospitals))
    hospitals.sort()
    return [{"label": i, "value": i} for i in hospitals]



@app.callback(
    Output('df_tab1', "data"),
    [
     Input("hospital-select1", "value"),
     ],
    #prevent_initial_call=True,
    )
def update_df1_tab1(hospitals):  ##!!
    
    if hospitals is None or hospitals == []:
        return None
    
    if isinstance(hospitals, str) == True:
        hospitals = [hospitals]
    
    for i, val in enumerate(hospitals):
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        
        if i == 0:
            main_df = tdf.copy(deep=True)
        else:
            main_df = pd.concat([main_df, tdf]) 
    
    
    return main_df.to_json()
    
    

@app.callback(
    Output("map_plot1", "figure"),
    [
     Input("df_tab1", "data"),
     Input("hospital-select1", "value"),
     ],
    )
def update_map_plot1(df, h):
    
    if df is None:
        figure = go.Figure()
        figure.add_trace(go.Scattermapbox(
        ),
        )
        
        figure.update_layout(
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken='pk.eyJ1Ijoia2xvY2V5IiwiYSI6ImNrYm9uaWhoYjI0ZDcycW56ZWExODRmYzcifQ.Mb27BYst186G4r5fjju6Pw',
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=39,
                    lon=-98
            ),
            pitch=20,
            zoom=3,
            style='light',
            )
        )
    
        figure.update_layout(
            height=300, 
            margin={"r":0,"t":0,"l":0,"b":0},
            )
    
        return figure
    
    df = pd.read_json(df)
    
    figure = go.Figure()
    
    figure.add_trace(go.Scattermapbox(
        lon = df["('Lon', 'Lon', 'Lon', 'Lon')"],
        lat = df["('Lat', 'Lat', 'Lat', 'Lat')"],
        text = df["('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')"],
               
        marker = dict(
            size = 10,
            color = 'rgb(0, 170, 255)',
            opacity = 0.8,

        ),
        ),
        )
        
    figure.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken='pk.eyJ1Ijoia2xvY2V5IiwiYSI6ImNrYm9uaWhoYjI0ZDcycW56ZWExODRmYzcifQ.Mb27BYst186G4r5fjju6Pw',
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=39,
                lon=-98
        ),
        pitch=20,
        zoom=3,
        style='light',
        )
    )

    figure.update_layout(
        height=300, 
        margin={"r":0,"t":0,"l":0,"b":0},
        )
    
    return figure

    
@app.callback( # Update Table 1
    Output("table1", "figure"),
    [
     Input('df_tab1', "data"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     ],
    )
def update_table1(main_df, var1, var2):
    
    if main_df is None or var1 is None or var2 is None:
        figure = go.Figure(data=[go.Table(
            header=dict(values=[
                'Provider name',
                'Fiscal year end date',
                'Variable of interest',
                ],
                fill_color='#b3d1ff',
                align='left'),
            ),
            ],
            )

        figure.update_layout(title_font=dict(size=14,
                        color="rgb(38, 38, 38)", 
                        ),
                        margin=dict(l=10, r=10, b=10, t=0),
                        paper_bgcolor="#f0f0f0",
                        plot_bgcolor="#f0f0f0",
                        height=300,
                        )
            
        return figure
    
    main_df = pd.read_json(main_df)
    if main_df.shape[0] == 0:
        figure = go.Figure(data=[go.Table(
            header=dict(values=[
                'Provider name',
                'Fiscal year end date',
                'Variable of interest',
                ],
                fill_color='#b3d1ff',
                align='left'),
            ),
            ],
            )

        figure.update_layout(title_font=dict(size=14,
                        color="rgb(38, 38, 38)", 
                        ),
                        margin=dict(l=10, r=10, b=10, t=0),
                        paper_bgcolor="#f0f0f0",
                        plot_bgcolor="#f0f0f0",
                        height=300,
                        )
            
        return figure
    
    var3 = re.sub(r'\([^)]*\)', '', var2)        
    table_df = pd.DataFrame(columns=[
                            'Provider name',
                            'Fiscal year end date',
                            ])
            
    table_df['Provider name'] = main_df["('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')"]
    table_df['Fiscal year end date'] = pd.to_datetime(main_df["('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')"]).dt.date
    
    str_ = var1 + "', '" + var2 + "')"
    column = [col for col in main_df.columns if col.endswith(str_)]  
    column = column[0]
    obs_y = main_df[column].tolist()     
    #obs_y = main_df.iloc[:, ((main_df.columns.get_level_values(2)==var1) & (main_df.columns.get_level_values(3)==var2))]                   
    #obs_y = list(obs_y.iloc[0:, 0].tolist())
    table_df[var3] = obs_y
                    
    table_df.sort_values(by=['Fiscal year end date'], ascending=[True])
    #dates, obs_y = map(list, zip(*sorted(zip(dates, obs_y), reverse=False)))
            
    figure = go.Figure(data=[go.Table(
        header=dict(values=list(table_df.columns),
                    fill_color='#b3d1ff',
                    align='left'),
        cells=dict(values=[table_df['Provider name'], 
                           table_df['Fiscal year end date'],
                           table_df[var3],
                           ],
                   fill_color='#e6f0ff',
                   align='left'))
        ])
            
    figure.update_layout(title_font=dict(size=14,
                         color="rgb(38, 38, 38)", 
                         ),
                         margin=dict(l=10, r=10, b=0, t=10),
                         paper_bgcolor="#f0f0f0",
                         plot_bgcolor="#f0f0f0",
                         height=300,
                         )

    return figure
    
    
    
@app.callback( # Update Line plot
    Output("cost_report_plot1", "figure"),
    [
     Input('df_tab1', "data"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     ],
    )
def update_cost_report_plot1(df, var1, var2):
    
    if df is None or var1 is None or var1 is None:
        fig = go.Figure(data=go.Scatter(x = [0], y = [0]))

        fig.update_yaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))
        fig.update_xaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))

        fig.update_layout(title_font=dict(size=14, 
                          color="rgb(38, 38, 38)", 
                          ),
                          showlegend=True,
                          margin=dict(l=100, r=10, b=10, t=10),
                          paper_bgcolor="#f0f0f0",
                          plot_bgcolor="#f0f0f0",
                          )
        
        return fig
         
    df = pd.read_json(df)
    if df.shape[0] == 0:
        fig = go.Figure(data=go.Scatter(x = [0], y = [0]))

        fig.update_yaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))
        fig.update_xaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))

        fig.update_layout(title_font=dict(size=14, 
                          color="rgb(38, 38, 38)", 
                          ),
                          showlegend=True,
                          margin=dict(l=100, r=10, b=10, t=10),
                          paper_bgcolor="#f0f0f0",
                          plot_bgcolor="#f0f0f0",
                          )
        
        return fig
        
    fig_data = []
    hospitals = sorted(list(set(df["('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')"].tolist())))
    
    for i, hospital in enumerate(hospitals):
        
        sub_df = df[df["('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')"] == hospital]
        #sub_df.sort_values(by=["('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')"],
        #                        ascending=[True], inplace=True)
            
        dates = sub_df["('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')"]
            
        str_ = var1 + "', '" + var2 + "')"
        column = [col for col in sub_df.columns if col.endswith(str_)]  
        column = column[0]
        obs_y = sub_df[column].tolist()     
        
        #dates, obs_y = map(list, zip(*sorted(zip(dates, obs_y), reverse=False)))
            
        fig_data.append(
                go.Scatter(
                    x=dates,
                    y=obs_y,
                    name=hospital,
                    mode="lines",
                )
            )
        
        var3 = re.sub(r'\([^)]*\)', '', var2)
        
        figure = go.Figure(
            data=fig_data,
            layout=go.Layout(
                transition = {'duration': 500},
                xaxis=dict(
                    title=dict(
                        text="<b>Date</b>",
                        font=dict(
                            family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                            " Helvetica, Arial, sans-serif",
                            size=18,
                        ),
                    ),
                    rangemode="tozero",
                    zeroline=True,
                    showticklabels=True,
                ),
                
                yaxis=dict(
                    title=dict(
                        text='<b>' + var1 + '<b>' + '<br>' + var3 + '<br>' + ' ' + '<br>',
                        font=dict(
                            family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                            " Helvetica, Arial, sans-serif",
                            size=14,
                            
                        ),
                    ),
                    rangemode="tozero",
                    zeroline=True,
                    showticklabels=True,
                    
                ),
                
                margin=dict(l=100, r=30, b=10, t=40),
                showlegend=True,
                height=400,
                paper_bgcolor="#f0f0f0",
                plot_bgcolor="#f0f0f0",
            ),
        )
        
        figure.update_layout(
            legend=dict(
                traceorder="normal",
                font=dict(
                    size=10,
                    color="rgb(38, 38, 38)"
                ),
                
            )
        )    
        
    return figure
    


@app.callback(
    Output("cost_report_plot2", "figure"),
    [
     Input('df_tab1', "data"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     ],
    )
def update_cost_report_plot2(main_df, var1, var2):
    
    figure = go.Figure(data=go.Scatter(x = [0], y = [0]))
        
    figure.update_yaxes(title_font=dict(size=14, 
                                     color="rgb(38, 38, 38)"))
    figure.update_xaxes(title_font=dict(size=14, 
                                     color="rgb(38, 38, 38)"))

    figure.update_layout(title_font=dict(size=14, 
                      color="rgb(38, 38, 38)", 
                      ),
                      showlegend=True,
                      margin=dict(l=100, r=10, b=10, t=10),
                      paper_bgcolor="#f0f0f0",
                      plot_bgcolor="#f0f0f0",
                      )
    
    if main_df is None or var1 is None or var2 is None:
        return figure
        
    else:    
        main_df = pd.read_json(main_df)
        if main_df.shape[0] == 0:
            return figure
        
        col_names = ['Fiscal Year End Date', 'Num and Name']
        new_df = pd.DataFrame(columns = col_names)
        
        dates = main_df["('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')"].tolist()
        new_df['Fiscal Year End Date'] = dates
        
        str_ = var1 + "', '" + var2 + "')"
        column = [col for col in main_df.columns if col.endswith(str_)]  
        column = column[0]
        new_df[var2] = main_df[column].tolist()
        
        new_df['Num and Name'] = main_df["('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')"].tolist()                   
        
        fig_data = []
        new_df['years'] = pd.to_datetime(new_df['Fiscal Year End Date']).dt.year
        years = list(set(new_df['years'].tolist()))
        
        try: 
            sub_df = new_df[new_df['years'] == max(years)]
        except:
            return figure
        
        obs_y = sub_df[var2].tolist()
        hospitals2 = sub_df['Num and Name'].tolist()
        
        
        fig_data.append(
            go.Bar(
                x=hospitals2,
                y=obs_y,
                name=max(years),
                #smarker_color=px.colors.sequential.Plasma,
            )
        )
            
        var3 = re.sub(r'\([^)]*\)', '', var2)
        figure = go.Figure(
            data=fig_data,
            layout=go.Layout(
                transition = {'duration': 500},
                xaxis=dict(
                    title=None,
                    rangemode="tozero",
                    zeroline=True,
                    showticklabels=True,
                    tickangle=0,
                ),
                
                yaxis=dict(
                    title=dict(
                        text='<b>' + var1 + '<b>' + '<br>' + var3 + '<br>' + ' ' + '<br>',
                        font=dict(
                            family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                            " Helvetica, Arial, sans-serif",
                            size=14,
                            
                        ),
                    ),
                    rangemode="tozero",
                    zeroline=True,
                    showticklabels=True,
                    
                ),
                
                
                
                margin=dict(l=100, r=10, b=10, t=40),
                height=600,
                paper_bgcolor="#f0f0f0",
                plot_bgcolor="#f0f0f0",
            ),
        )
        
        for year in years:
            if year != max(years):
                
                sub_df = new_df[new_df['years'] == year]
                obs_y = sub_df[var2].tolist()
                hospitals2 = sub_df['Num and Name'].tolist()
                
                figure.add_trace(go.Bar(
                    x = hospitals2,
                    y = obs_y,
                    name = year))
        
        
        figure.update_layout(showlegend=True, 
                             xaxis_tickangle=-45,
                             xaxis_tickfont_size=10,
                             barmode='stack',
                             xaxis={'categoryorder':'total descending'})
        
        return figure
    
   
#########################################################################################



###############################    TAB 2    #############################################
#########################################################################################

@app.callback(
    Output("df_tab2", "data"),
    [
     Input("focal-hospital-select2", "value"),
     ],
    )
def update_hospital(hospital):
    
    if hospital is None:
        return None
        
    prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', hospital)
        
    url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
    df = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        
    return df.to_json()
 

@app.callback( # Update available sub_categories
    Output('categories-select22', 'options'),
    [
     Input('categories-select2', 'value'),
     Input('df_tab2', "data"),
     ],
    )
def update_output7(value, df):
    main_df2 = main_df.iloc[:, (main_df.columns.get_level_values(2)==value)]
    sub_cat = main_df2.columns.get_level_values(3).tolist()
    del main_df2
    
    if df is not None:
        df = pd.read_json(df)
        df.dropna(axis=1, thresh = df.shape[0], inplace=True) # 
        cols1 = list(df)
        cols2 = []
        for c in cols1:
            s = c.split("', ")[-1]
            s = s[1:-2]
            cols2.append(s)
            
        sub_categories = []
        for c in sub_cat:
            if c in cols2:
                sub_categories.append(c)
    else:
        sub_categories = sub_cat
    
    #sub_categories = sorted(sub_categories)
    return [{"label": i, "value": i} for i in sub_categories]


@app.callback( # Select sub-category
    Output('categories-select22', 'value'),
    [
     Input('categories-select22', 'options'),
     ],
    )
def update_output8(available_options):
    try:
        #available_options = available_options[0]['value']
        #available_options = sorted(available_options)
        return available_options[0]['value']
    except:
        return 'NUMBER OF BEDS'
    
    

@app.callback( # Update available sub_categories
    Output('categories-select22-2', 'options'),
    [
     Input('categories-select2-2', 'value'),
     Input('df_tab2', "data"),
     ],
    )
def update_output9(value, df):
    main_df2 = main_df.iloc[:, (main_df.columns.get_level_values(2)==value)]
    sub_cat = main_df2.columns.get_level_values(3).tolist()
    del main_df2
    
    if df is not None:
        df = pd.read_json(df)
        df.dropna(axis=1, thresh = df.shape[0], inplace=True) # 
        cols1 = list(df)
        cols2 = []
        for c in cols1:
            s = c.split("', ")[-1]
            s = s[1:-2]
            cols2.append(s)
            
        sub_categories = []
        for c in sub_cat:
            if c in cols2:
                sub_categories.append(c)
    else:
        sub_categories = sub_cat
    
    #sub_categories = sorted(sub_categories)
    return [{"label": i, "value": i} for i in sub_categories]



@app.callback( # Select sub-category
    Output('categories-select22-2', 'value'),
    [
     Input('categories-select22-2', 'options'),
     ],
    )
def update_output10(available_options):
    try:
        return available_options[0]['value']
    except:
        return 'NUMBER OF BEDS'
    
    

@app.callback( # Update Line plot
    Output("cost_report_plot3", "figure"),
    [
     Input("df_tab2", "data"),
     Input('categories-select2', 'value'),
     Input('categories-select22', 'value'),
     Input('categories-select2-2', 'value'),
     Input('categories-select22-2', 'value'),
     Input('trendline-1', 'value'),
     ],
    )
def update_cost_report_plot3(df, xvar1, xvar2, yvar1, yvar2, trendline):
    
    
    if df is None or xvar1 is None or xvar2 is None or yvar1 is None or yvar2 is None or yvar2 == 'NUMBER OF BEDS':
            
            tdf = pd.DataFrame(columns=['x', 'y'])
            tdf['x'] = [0]
            tdf['y'] = [0]
            fig = px.scatter(tdf, x = 'x', y = 'y')

            fig.update_yaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))
            fig.update_xaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))

            fig.update_layout(title_font=dict(size=14, 
                          color="rgb(38, 38, 38)", 
                          ),
                          showlegend=True,
                          margin=dict(l=100, r=10, b=10, t=10),
                          paper_bgcolor="#f0f0f0",
                          plot_bgcolor="#f0f0f0",
                          )
        
            return fig
            
    df = pd.read_json(df)
    
    fig_data = []
    
    dates = df["('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')"].tolist()
    #df['years'] = pd.to_datetime(dates).dt.year
    
    #headers = list(set(list(df)))
    
    str_ = xvar1 + "', '" + xvar2 + "')"
    
    column = [col for col in df.columns if col.endswith(str_)]  
    column = column[0]
    x = df[column].tolist()
    
    str_ = yvar1 + "', '" + yvar2 + "')"
    column = [col for col in df.columns if col.endswith(str_)]  
    column = column[0]
    y = df[column].tolist()
    
    hospital = list(set(df["('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')"].tolist()))                 
    
    fig_data = []
        
    x, y, dates = map(list, zip(*sorted(zip(x, y, dates), reverse=False)))
        
    fig_data.append(
                go.Scatter(
                    x=x,
                    y=y,
                    name=hospital[0],
                    mode="markers",
                    text=dates,
                )
            )
        
    tdf = pd.DataFrame(columns = ['x', 'y'])
    tdf['x'] = x
    tdf['y'] = y
    tdf['dates'] = dates
    tdf.dropna(how='any', inplace=True)
    x = tdf['x']
    y = tdf['y']
    dates = tdf['dates'].tolist()
        
    ty = []
    r2 = ''
        
    if x.tolist() == [] or y.tolist() == []:
        slope, intercept, r_value, p_value, std_err = np.nan, np.nan, np.nan, np.nan, np.nan
        r2 = np.nan
        
    else:
        if trendline == 'linear':
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            ty = intercept + slope*np.array(x)
                
            r2 = obs_pred_rsquare(y, ty)
            r2 = np.round(100*r2, 1)
                
        elif trendline == 'locally weighted':
            lowess = sm.nonparametric.lowess
            ty = lowess(y, x)
            ty = np.transpose(ty)
            ty = ty[1]
                
            r2 = obs_pred_rsquare(y, ty)
            r2 = np.round(100*r2, 1)
                
        elif trendline == 'quadratic':
            z = np.polyfit(x, y, 2).tolist()
            p = np.poly1d(z)
            ty = p(x)
                
            r2 = obs_pred_rsquare(y, ty)
            r2 = np.round(100*r2, 1)
                
        elif trendline == 'cubic':
            z = np.polyfit(x, y, 3).tolist()
            p = np.poly1d(z)
            ty = p(x)
                
            r2 = obs_pred_rsquare(y, ty)
            r2 = np.round(100*r2, 1)
                        
        if x.tolist() != [] and y.tolist() != []:
            fig_data.append(
                go.Scatter(
                x=x,
                y=ty,
                mode='lines',
                marker=dict(color="#99ccff"),
                )
            )
            
        #var3 = re.sub(r'\([^)]*\)', '', var2)
        
    figure = go.Figure(
        data=fig_data,
        layout=go.Layout(
            transition = {'duration': 500},
            xaxis=dict(
                title=dict(
                    text='<b>' + xvar1 + '<b>' + '<br>' + xvar2 + '<br>' + ' ' + '<br>',
                    font=dict(
                        family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                        " Helvetica, Arial, sans-serif",
                        size=14,
                    ),
                ),
                #rangemode="tozero",
                zeroline=True,
                showticklabels=True,
            ),
                
            yaxis=dict(
                title=dict(
                    text='<b>' + yvar1 + '<b>' + '<br>' + yvar2 + '<br>' + ' ' + '<br>',
                    font=dict(
                        family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                        " Helvetica, Arial, sans-serif",
                        size=14,
                            
                    ),
                ),
                #rangemode="tozero",
                zeroline=True,
                showticklabels=True,
                    
            ),
                
            margin=dict(l=80, r=10, b=80, t=60),
            showlegend=False,
            height=500,
            paper_bgcolor="#f0f0f0",
            plot_bgcolor="#f0f0f0",
        ),
    )
        
    if x.tolist() != [] and y.tolist() != []:
        figure.update_layout(
            title="Percent variation explained by the model: " + str(r2),
            font=dict(
                size=10,
                color="rgb(38, 38, 38)"
                ),
            )
        
    return figure



@app.callback( # Update Line plot
    Output("cost_report_plot4", "figure"),
    [
     Input("df_tab2", "data"),
     Input('categories-select2-3', 'value'),
     ],
    )
def update_cost_report_plot4(df, var1):
    if df is None or var1 is None:
            
         fig = go.Figure(data=go.Scatter(x = [0], y = [0]))

         fig.update_yaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))
         fig.update_xaxes(title_font=dict(size=14, 
                                         #family='sans-serif', 
                                         color="rgb(38, 38, 38)"))

         fig.update_layout(title_font=dict(size=14, 
                          color="rgb(38, 38, 38)", 
                          ),
                          showlegend=True,
                          margin=dict(l=100, r=10, b=10, t=10),
                          paper_bgcolor="#f0f0f0",
                          plot_bgcolor="#f0f0f0",
                          )
                          
         return fig
            
    df = pd.read_json(df)
    headers = list(set(list(df)))
    
    columns = []
    for h in headers:
        if var1 in h:
            columns.append(h)
    
    date_col = "('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')"
    
    df = df.filter(items=columns + [date_col], axis=1)    
    df.dropna(how='all', axis=0, inplace=True)
    #df['years'] = pd.to_datetime(df[date_col].tolist()).dt.year
    fig_data = []
        
    for c in columns:
        
        x_ls = list(set(df[c].tolist()))
        x = [x for x in x_ls if x == x]
        if len(x) == 0:
            continue
        
        s = c.split("', ")[-1]
        s = s[1:-2]
        fig_data.append(
                go.Bar(
                x = df[date_col],
                y = df[c],
                #hovertext=c,
                name=s,
                #marker_color='#99ccff',
                )
            )
        
    figure = go.Figure(
    data=fig_data,
    layout=go.Layout(
    transition = {'duration': 500},
    xaxis=dict(
        title=dict(
        #text='<b>' + xvar1 + '<b>' + '<br>' + xvar2 + '<br>' + ' ' + '<br>',
        font=dict(
            family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
            " Helvetica, Arial, sans-serif",
            size=14,
            ),
        ),
        rangemode="tozero",
        zeroline=True,
        showticklabels=True,
        ),
                
    yaxis=dict(
        title=dict(
            #text='<b>' + yvar1 + '<b>' + '<br>' + yvar2 + '<br>' + ' ' + '<br>',
            font=dict(
                family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                " Helvetica, Arial, sans-serif",
                size=14,
                            
                ),
            ),
        rangemode="tozero",
        zeroline=True,
        showticklabels=True,
                    
        ),
                
    margin=dict(l=40, r=10, b=80, t=40),
    showlegend=True,
    height=590,
    paper_bgcolor="#f0f0f0",
    plot_bgcolor="#f0f0f0",
    ),
    )
        
    ypos = -0.1
    figure.update_layout(
        legend=dict(
            orientation = "h",
            y = ypos,
            yanchor = "top",
            xanchor="left",
            traceorder = "normal",
            font = dict(
                size = 10,
                color = "rgb(38, 38, 38)"
            ),
                
        )
    )
        
    figure.update_layout(barmode='stack', 
                         #xaxis_tickangle=-45,
                         font=dict(
                         size=10,
                         color="rgb(38, 38, 38)",
                         ),
                         )
        
    return figure
    

@app.callback( # Update available sub_categories
    Output('trendline-1', 'options'),
    [
     Input('trendline-1', 'value'),
     ],
    )
def update_output11(value):
    options = ['linear', 'locally weighted',
               'quadratic', 'cubic']
    
    return [{"label": i, "value": i} for i in options]
'''





#########################################################################################





###############################    TAB 1: Text    #######################################
#########################################################################################
@app.callback(
    Output("text1", "children"),
    [
     Input("hospital-select1", "value"),
     Input('states-select1', 'value'),
     Input('beds1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     ],
    )
def update_text1(hospitals2, states_val, beds_val, htype_vals, ctype_vals):
    
    if hospitals2 is None:
        return '0 hospitals selected'
    
    elif isinstance(hospitals2, str) == True:
        hospitals2 = [hospitals2]
    
    low, high = beds_val
    h3 = []
    
    for i, h in enumerate(HOSPITALS):
        if h in hospitals2:    
            b = beds[i]
            s = states[i]
            ht = htypes[i]
            ct = ctypes[i]
            if b > low and b < high:
                if s in states_val:
                    if ht in htype_vals:
                        if ct in ctype_vals:
                            h3.append(h)
            
    hospitals2 = list(set(h3))
    hospitals2.sort()
    
    text = str(len(hospitals2)) + ' hospitals selected'
    return text



@app.callback(
    Output("data_link", "href"),
    [
     Input("hospital-select1", "value"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     Input('states-select1', 'value'),
     #Input('beds', 'value'),
     #Input('hospital_type', 'value'),
     ],
    )
def update_text2(hospitals2, var1, var2, states): #, beds, htypes):
    
    if isinstance(hospitals2, str) == True:
        hospitals2 = [hospitals2]
    if hospitals2 == [] or var1 is None:
        csv_string = main_df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
        return csv_string
        
    main_df2 = main_df.copy(deep=True)
    for val in hospitals2:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        main_df2 = pd.concat([main_df2, tdf]) 
        
    col_names =  ['Fiscal Year End Date', var2, 'Num and Name']
    new_df = pd.DataFrame(columns = col_names)
    
    FY_END_DT = main_df2.iloc[:, 
                ((main_df2.columns.get_level_values(0)=='FY_END_DT') & (main_df2.columns.get_level_values(1)=='Fiscal Year End Date '))]
    dates = list(FY_END_DT.iloc[0:, 0].tolist())
    new_df['Fiscal Year End Date'] = dates
    
    S3_1_C3_14 = main_df2.iloc[:, 
                ((main_df2.columns.get_level_values(2)==var1) & (main_df2.columns.get_level_values(3)==var2))]
    new_df[var2] = list(S3_1_C3_14.iloc[0:, 0].tolist())
    
    S2_1_C2_2 = main_df2.iloc[:, 
                ((main_df2.columns.get_level_values(0)=='Num and Name') & (main_df2.columns.get_level_values(1)=='Num and Name'))]                   
    new_df['Num and Name'] = list(S2_1_C2_2.iloc[0:, 0].tolist())
    
    new_df = new_df[new_df['Num and Name'].isin(hospitals2)]
    new_df['years'] = pd.to_datetime(new_df['Fiscal Year End Date']).dt.year
    new_df = new_df[new_df['years'] == 2021]
    max_val = 0
    max_prv = str()
    min_val = 10**10
    min_prv = str()

    for i, hospital in enumerate(hospitals2):
            
        sub_df = new_df[new_df['Num and Name'] == hospital]
        try:
            obs_y = sub_df[var2].iloc[0]
        
            if obs_y > max_val:
                max_val = obs_y
                max_prv = hospital
            
            if obs_y < min_val:
                min_val = obs_y
                min_prv = hospital
        except:
            pass
            
    max_val = '{:,}'.format(max_val)
    min_val = '{:,}'.format(min_val)
    
    col = main_df2.iloc[:, main_df2.columns.get_level_values(0)=='FY_END_DT']
    col = list(col.iloc[0:, 0].tolist())
    
    main_df2 = main_df2.drop('FY_END_DT', axis = 1, level = 0)
    main_df2['FY_END_DT', 'Fiscal Year End Date',
             'HOSPITAL IDENTIFICATION INFORMATION',
             'Fiscal Year End Date (FY_END_DT)'] = col

    col = main_df2.iloc[:, main_df2.columns.get_level_values(0)=='Num and Name']
    col = list(col.iloc[0:, 0].tolist())
    
    main_df2 = main_df2.drop('Num and Name', axis = 1, level = 0)
    main_df2['Num and Name', 'Num and Name',
             'Num and Name', 'Num and Name'] = col
    
    ls = list(main_df2.columns.get_level_values(0))
    ls.reverse()
    
    main_df2 = main_df2.reindex(ls, axis=1, level=0)
    
    csv_string = main_df2.to_csv(index=True, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    
    del main_df2
    
    return csv_string
#########################################################################################
'''    



# Run the server
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug = False) # modified to run on linux server

