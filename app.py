import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import warnings
import sys
import re
import csv

from urllib.request import urlopen
import urllib
from math import isnan

import numpy as np
import statsmodels.api as sm
from scipy import stats

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)


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
            html.H5("Healthcare financial insights", style={
            'textAlign': 'left',
        }),
           html.P(" Dive into healthcare provider financial reports." +
                  " This app combines data from the Healthcare Cost Report Information System (HCRIS)" +
                  " with additional data from the Centers for Medicare & Medicaid Services (CMS)." +
                  " Until now, using these data meant tackling complex datasets with expensive software."
                  , style={
            'textAlign': 'left',
        }),  
        ],
    )

def description_card2():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card2",
        children=[
            html.H5("Insights into Healthcare Cost Reports", style={
            'textAlign': 'left',
        }),
           html.P(" Dive into healthcare provider financial reports." +
                  " This app combines data from the Healthcare Cost Report Information System (HCRIS)" +
                  " with additional data from the Centers for Medicare & Medicaid Services (CMS)." +
                  " Until now, using these data meant tackling complex datasets with expensive software." +
                  " This app allows you to explore 2,000+ variables from over 9,000+ hospitals.",
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
            
            html.P("Select a set of hospitals to compare"),
            dcc.Dropdown(
                id="hospital-select1",
                options=[{"label": i, "value": i} for i in HOSPITALS],
                multi=True,
                value=None,
                optionHeight=50,
                style={
                    #'width': '320px',
                    'font-size': "90%",
                    }
            ),
            html.Br(),
            
            html.P("Select a report category to analyze by"),
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
            html.P("Select a category and sub-category for your x-variable"),
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
            
            
            html.P("Select a category and sub-category for your y-variable"),
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
            html.P("Select a category"),
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



def table1(hospitals2, var1, var2):
    if isinstance(hospitals2, str) == True:
        hospitals2 = [hospitals2]

    if hospitals2 == [] or hospitals2 == None or var1 is None or states == None:
        
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
    
    new_df = main_df.copy(deep=True)
    for val in hospitals2:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        new_df = pd.concat([new_df, tdf])
        
    var3 = re.sub(r'\([^)]*\)', '', var2)
    var3 = var1 + ': ' + var3,
    
    table_df = pd.DataFrame(columns=[
                    'Provider name',
                    'Fiscal year end date',
                    var3,
                    ])
    
    table_df['Provider name'] = new_df[('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')]
    
    table_df['Fiscal year end date'] = pd.to_datetime(new_df[('FY_END_DT', 'Fiscal Year End Date ', 
                                               'HOSPITAL IDENTIFICATION INFORMATION', 
                                               'Fiscal Year End Date  (FY_END_DT)')]).dt.date
    
    
    obs_y  = new_df.iloc[:, ((new_df.columns.get_level_values(2)==var1) & (new_df.columns.get_level_values(3)==var2))]                   
    obs_y = list(obs_y.iloc[0:, 0].tolist())
    table_df[var3] = obs_y
            
    table_df.sort_values(by=['Fiscal year end date'], ascending=[True])
    #dates, obs_y = map(list, zip(*sorted(zip(dates, obs_y), reverse=False)))
    #var3 = re.sub(r'\([^)]*\)', '', var2)
    
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
    

    
def cost_report_plot1(hospitals2, var1, var2):
    
    if isinstance(hospitals2, str) == True:
        hospitals2 = [hospitals2]

    if hospitals2 == [] or hospitals2 == None or var1 is None or states == None:
        
        #ttdf = pd.DataFrame(columns=['x', 'y'])
        #ttdf['x'] = [0]
        #ttdf['y'] = [0]
        #fig = px.scatter(ttdf, x = 'x', y = 'y')
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
        
    
    new_df = main_df.copy(deep=True)
    for val in hospitals2:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        new_df = pd.concat([new_df, tdf])
        
    fig_data = []
    for i, hospital in enumerate(hospitals2):
            
        sub_df = new_df[new_df[('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')] == hospital]
        sub_df.sort_values(by=[('FY_END_DT', 
                                'Fiscal Year End Date ', 
                                'HOSPITAL IDENTIFICATION INFORMATION', 
                                'Fiscal Year End Date  (FY_END_DT)')],
                               ascending=[True])
        
        dates = sub_df[('FY_END_DT', 
                        'Fiscal Year End Date ', 
                        'HOSPITAL IDENTIFICATION INFORMATION', 
                        'Fiscal Year End Date  (FY_END_DT)')]
        
        obs_y  = sub_df.iloc[:, 
                ((main_df.columns.get_level_values(2)==var1) & (main_df.columns.get_level_values(3)==var2))]                   
        obs_y = list(obs_y.iloc[0:, 0].tolist())
        
        dates, obs_y = map(list, zip(*sorted(zip(dates, obs_y), reverse=False)))
        
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
    
    figure.update_xaxes(range=[pd.to_datetime('2010-01-01'), pd.to_datetime('2019-01-01')])
    
    return figure





def cost_report_plot2(hospitals2, var1, var2):
    
    if isinstance(hospitals2, str) == True:
        hospitals2 = [hospitals2]

    if hospitals2 == [] or hospitals2 == None or var1 is None or states == None:
        
        #ttdf = pd.DataFrame(columns=['x', 'y'])
        #ttdf['x'] = [0]
        #ttdf['y'] = [0]
        #fig = px.scatter(ttdf, x = 'x', y = 'y')
        fig = go.Figure(data=go.Scatter(x = [0], y = [0]))
        
        fig.update_yaxes(title_font=dict(size=14, 
                                     color="rgb(38, 38, 38)"))
        fig.update_xaxes(title_font=dict(size=14, 
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
        
        
    main_df2 = main_df.copy(deep=True)
    for val in hospitals2:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        main_df2 = pd.concat([main_df2, tdf])
        
    col_names = ['Fiscal Year End Date', var2, 'Num and Name']
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

    del main_df2
    
    fig_data = []
    new_df['years'] = pd.to_datetime(new_df['Fiscal Year End Date']).dt.year
    years = list(set(new_df['years'].tolist()))
    
    try: 
        sub_df = new_df[new_df['years'] == max(years)]
    except:
        return go.Figure()
    
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





def cost_report_plot3(hospital, xvar1, xvar2, yvar1, yvar2, trendline):    
    
    if hospital == None or xvar1 is None or xvar2 is None or yvar1 is None or yvar2 is None:
        
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
        
    
    new_df = main_df.copy(deep=True)
    for val in [hospital]:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        new_df = pd.concat([new_df, tdf])
        
    fig_data = []
    
    x = new_df.iloc[:, 
                ((new_df.columns.get_level_values(2)==xvar1) & (new_df.columns.get_level_values(3)==xvar2))]                   
    x = list(x.iloc[0:, 0].tolist())
    
    y = new_df.iloc[:, 
                ((new_df.columns.get_level_values(2)==yvar1) & (new_df.columns.get_level_values(3)==yvar2))]                   
    y = list(y.iloc[0:, 0].tolist())
    
    new_df[('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')] = pd.to_datetime(new_df[('FY_END_DT', 'Fiscal Year End Date ', 
                                               'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')]).dt.date
    dates = new_df[('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')].tolist()
    
    
    x, y, dates = map(list, zip(*sorted(zip(x, y, dates), reverse=False)))
    
    fig_data.append(
            go.Scatter(
                x=x,
                y=y,
                name=hospital,
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
                rangemode="tozero",
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
                rangemode="tozero",
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
    
    figure.update_layout(
        title="Percent variation explained by the model: " + str(r2),
        font=dict(
                size=10,
                color="rgb(38, 38, 38)"
            ),
        )
    
    #figure.update_layout(
    #    legend=dict(
    #        traceorder="normal",
    #        font=dict(
    #            size=10,
    #            color="rgb(38, 38, 38)"
    #        ),
            
    #    )
    #)
    
    return figure




def cost_report_plot4(hospital, var1):    
    
    if hospital == None or var1 is None:
        
        #ttdf = pd.DataFrame(columns=['x', 'y'])
        #ttdf['x'] = [0]
        #ttdf['y'] = [0]
        #fig = px.scatter(ttdf, x = 'x', y = 'y')
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
        
    
    #sub_df = main_df[main_df[('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')] == hospital]
    
    sub_df = main_df.copy(deep=True)
    for val in [hospital]:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        sub_df = pd.concat([sub_df, tdf])
        
        
    sub_df1 = sub_df.iloc[:, sub_df.columns.get_level_values(2) == var1]
    sub_df1 = sub_df1.droplevel([0,1,2], axis=1).reset_index()
    
    dates = sub_df[('FY_END_DT', 'Fiscal Year End Date ', 'HOSPITAL IDENTIFICATION INFORMATION', 'Fiscal Year End Date  (FY_END_DT)')].tolist()
    
    sub_df1['Fiscal Year End Date'] = list(dates)
    sub_df1.dropna(how='any', axis=1, inplace=True)
    
    fig_data = []
    col_list = list(sub_df1)
    col_list = col_list[1:-1]
    
    for c in col_list:
        fig_data.append(
            go.Bar(
            x = sub_df1['Fiscal Year End Date'],
            y = sub_df1[c],
            hovertext=c,
            name=c,
            #marker_color='#99ccff',
            )
        )
    
    #var3 = re.sub(r'\([^)]*\)', '', var2)
    
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
    
    figure.update_layout(
        #title="Percent variation explained by the model: " + str(r2),
        
        )
    
    
    return figure





def map1(hospitals2, var1, var2):
    
    if isinstance(hospitals2, str) == True:
        hospitals2 = [hospitals2]

    if hospitals2 == [] or hospitals2 == None or var1 is None or states == None:
        
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
    
    
    new_df = main_df.copy(deep=True)
    for val in hospitals2:
        
        prvdr = re.sub('\ |\?|\.|\!|\/|\;|\:', '', val)
        
        url = 'https://raw.githubusercontent.com/klocey/HCRIS-databuilder/master/provider_data/' + prvdr + '.csv'
        tdf = pd.read_csv(url, index_col=[0], header=[0,1,2,3])
        new_df = pd.concat([new_df, tdf])
        
    figure = go.Figure()
    
    figure.add_trace(go.Scattermapbox(
        lon = new_df[('Lon', 'Lon', 'Lon', 'Lon')],
        lat = new_df[('Lat', 'Lat', 'Lat', 'Lat')],
        text = new_df[('Num and Name', 'Num and Name', 'Num and Name', 'Num and Name')], #+ ', ' + 
               #new_df[('S2_1_C2_2', 'Hospital State', , 'Hospital State (S2_1_C2_2)')],
               
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
    
    
    
    
    
    
########################### DASH APP LAYOUT ##################################


app.layout = html.Div([
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
                    [html.B(str(len(list(set(HOSPITALS)))) + " hospitals available", style={'fontSize':16}),
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
                            id='data_link', download="Cost_Reports_Full.csv",
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
        
        dcc.Tab(label='Single Provider Analysis',
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
            id="right-column2",
            className="five columns",
            children=[
                
                html.Div(
                    id="single_hospital_cost_report_plot3",
                    children=[
                        generate_control_card3(),
                        #html.B("Y vs. X"),
                        #html.Hr(),
                        dcc.Graph(id="cost_report_plot3"),
                        generate_control_card4(),
                    ],
                    style={'width': '110%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
                                 'display': 'inline-block',
                                 'height': '770px',
                                 #'fontSize':16
                            },
                    ),
                ],                
            ),
        
        html.Div(
            id="right-column3",
            className="seven columns",
            children=[
                
                html.Div(
                    id="single_hospital_cost_report_plot4",
                    children=[
                        generate_control_card5(),
                        #html.B("Y vs. X"),
                        #html.Hr(),
                        dcc.Graph(id="cost_report_plot4"),
                    ],
                    style={'width': '85%', 'display': 'inline-block',
                                 'border-radius': '15px',
                                 'box-shadow': '1px 1px 1px grey',
                                 'background-color': '#f0f0f0',
                                 'padding': '10px',
                                 'margin-bottom': '10px',
                                 'margin-left': '60px',
                                 'display': 'inline-block',
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


###############################    Tab 1: MAP    ########################################
#########################################################################################
@app.callback( # Update Map
    Output("map_plot1", "figure"),
    [
     Input("hospital-select1", "value"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     Input('states-select1', 'value'),
     Input('beds1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     
     ],
    )
def update_map_plot1(hospitals2, var1, var2, states_val, beds_val, htype_vals, ctype_vals):
    
    low, high = beds_val
    h3 = []
    
    if states_val == None:
        return map1(hospitals2, var1, var2)
    
    else:
        try:
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
            
        except:
            hospitals2 = None
         
        return map1(hospitals2, var1, var2)
#########################################################################################
    
    
    
    
    
###############################    TAB 1    #############################################
#########################################################################################
@app.callback( # Updated number of beds text
    Output('Filterbeds1', 'children'),
    [
     Input('beds1', 'value'),
     ],
    )
def update_output1(value):
    return 'Filter on number of beds: {}'.format(value)



@app.callback( # Updated number of beds text
    Output('Filterbeds2', 'children'),
    [
     Input('beds2', 'value'),
     ],
    )
def update_output6(value):
    return 'Filter on number of beds: {}'.format(value)



@app.callback( # Update hospitals based on states, type, and beds
    Output('hospital-select1', 'options'),
    [
     Input('beds1', 'value'),
     Input('states-select1', 'value'),
     Input('hospital-select1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     ],
    )
def update_output2(value, states_vals, hospitals2, htype_vals, ctype_vals):
    low, high = value
    h3 = []
    for i, h in enumerate(HOSPITALS):
        b = beds[i]
        s = states[i]
        ht = htypes[i]
        ct = ctypes[i]
        if b > low and b < high:
            if s in states_vals:
                if ht in htype_vals:
                    if ct in ctype_vals:
                        h3.append(h)
            
    hospitals2 = list(set(h3))
    hospitals2.sort()
    return [{"label": i, "value": i} for i in hospitals2]



@app.callback( # Update available sub_categories
    Output('categories-select11', 'options'),
    [
     Input('categories-select1', 'value'),
     ],
    )
def update_output3(value):
    main_df2 = main_df.iloc[:, (main_df.columns.get_level_values(2)==value)]
    sub_categories = main_df2.columns.get_level_values(3).tolist()
    del main_df2
    return [{"label": i, "value": i} for i in sub_categories]



@app.callback( # Select sub-category
    Output('categories-select11', 'value'),
    [
     Input('categories-select11', 'options'),
     ],
    )
def update_output4(available_options):
    try:
        return available_options[0]['value']
    except:
        return 'NUMBER OF BEDS'
    
    

@app.callback( # Update Table 1
    Output("table1", "figure"),
    [
     Input("hospital-select1", "value"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     Input('states-select1', 'value'),
     Input('beds1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     ],
    )
def update_table1(hospitals2, var1, var2, states_val, beds_val, htype_vals, ctype_vals):
    
    low, high = beds_val
    h3 = []
    
    if states_val == None:
        return cost_report_plot1(hospitals2, var1, var2)
    
    else:
        try:
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
            
        except:
            hospitals2 = None
         
        return table1(hospitals2, var1, var2)
    
    
    
@app.callback( # Update Line plot
    Output("cost_report_plot1", "figure"),
    [
     Input("hospital-select1", "value"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     Input('states-select1', 'value'),
     Input('beds1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     ],
    )
def update_cost_report_plot1(hospitals2, var1, var2, states_val, beds_val, htype_vals, ctype_vals):
    
    low, high = beds_val
    h3 = []
    
    if states_val == None:
        return cost_report_plot1(hospitals2, var1, var2)
    
    else:
        try:
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
            
        except:
            hospitals2 = None
         
        return cost_report_plot1(hospitals2, var1, var2)



@app.callback(
    Output("cost_report_plot2", "figure"),
    [
     Input("hospital-select1", "value"),
     Input('categories-select1', 'value'),
     Input('categories-select11', 'value'),
     Input('states-select1', 'value'),
     Input('beds1', 'value'),
     Input('hospital_type1', 'value'),
     Input('control_type1', 'value'),
     ],
    )
def update_cost_report_plot2(hospitals2, var1, var2, states_val, beds_val, htype_vals, ctype_vals):
    
    low, high = beds_val
    h3 = []
    
    if states_val == None:
        return cost_report_plot1(hospitals2, var1, var2)
    
    else:
        try:
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
            
        except:
            hospitals2 = None
        
        return cost_report_plot2(hospitals2, var1, var2)
#########################################################################################



###############################    TAB 2    #############################################
#########################################################################################
'''
@app.callback( # Update hospitals based on states, type, and beds
    Output('focal-hospital-select2', 'value'),
    [
     Input('focal-hospital-select2', 'value'),
     ],
    )
def update_output5(hospital):
    if hospital == None:
        hospital = HOSPITALS[0]
    h = [hospital]
    return hospital #[{"label": i, "value": i} for i in h]
'''

    
@app.callback( # Update available sub_categories
    Output('categories-select22', 'options'),
    [
     Input('categories-select2', 'value'),
     ],
    )
def update_output7(value):
    main_df2 = main_df.iloc[:, (main_df.columns.get_level_values(2)==value)]
    sub_categories = main_df2.columns.get_level_values(3).tolist()
    del main_df2
    return [{"label": i, "value": i} for i in sub_categories]



@app.callback( # Select sub-category
    Output('categories-select22', 'value'),
    [
     Input('categories-select22', 'options'),
     ],
    )
def update_output8(available_options):
    try:
        return available_options[0]['value']
    except:
        return 'NUMBER OF BEDS'
    
    

@app.callback( # Update available sub_categories
    Output('categories-select22-2', 'options'),
    [
     Input('categories-select2-2', 'value'),
     ],
    )
def update_output9(value):
    main_df2 = main_df.iloc[:, (main_df.columns.get_level_values(2)==value)]
    sub_categories = main_df2.columns.get_level_values(3).tolist()
    del main_df2
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
     Input('focal-hospital-select2', 'value'),
     Input('categories-select2', 'value'),
     Input('categories-select22', 'value'),
     Input('categories-select2-2', 'value'),
     Input('categories-select22-2', 'value'),
     Input('trendline-1', 'value'),
     ],
    )
def update_cost_report_plot3(hospital, xvar1, xvar2, yvar1, yvar2, trendline):
    return cost_report_plot3(hospital, xvar1, xvar2, yvar1, yvar2, trendline)



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





@app.callback( # Update Line plot
    Output("cost_report_plot4", "figure"),
    [
     Input('focal-hospital-select2', 'value'),
     Input('categories-select2-3', 'value'),
     ],
    )
def update_cost_report_plot4(hospital, var1):
    return cost_report_plot4(hospital, var1)



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
    new_df = new_df[new_df['years'] == 2019]
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
    text2 = '2019 Maximum value: ' + max_prv + ' ' + str(max_val) 
    text3 = '2019 Minimum value: ' + min_prv + ' ' + str(min_val)
    
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
    



# Run the server
if __name__ == "__main__":
    app.run_server(host='127.0.0.1', port=8050, debug=True)
