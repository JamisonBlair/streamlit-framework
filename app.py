import pandas as pd
import streamlit as st
import os
from dotenv import dotenv_values
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter
from datetime import datetime


@st.cache
def get_df(query):
    '''
    Parameters
    ----------
    query : str
        takes and AlphaVantage query and returns the full data as a
        pandas dataframe.

    Returns
    -------
    pandas DataFrame

    '''
    return pd.read_csv(query)

def get_month_data(df, month, year):
    '''

    Parameters
    ----------
    df : DataFrame
        The full DataFrame of (adjusted) daily stocks from queried ticker.
    month : str
        Month wanted to query.
    year : str
        Year wanted to query.

    Returns
    -------
    DataFrame
    
        A df of the dates, closing, and adjusted closing stock prices for the month and ticker queried.
    '''
    #A dict to go from month name to number
    month_to_num = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
                    'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    
    #the high and low months from the dates we want.
    mo_low = month_to_num[month]
    mo_hi_int = (int(mo_low) % 12) + 1
    if mo_hi_int < 10:
        mo_high = '0'+str(mo_hi_int)
    else:
        mo_high = str(mo_hi_int)
    
    #get the high and low dates to compare
    date_low = f'{year}-{mo_low}'   
    if mo_high == '01':
        year_high = str(int(year)+1)
    else:
        year_high = year
    date_high = f'{year_high}-{mo_high}'
    
    #return the sliced df from with the specified high/low dates
    return df[(df['timestamp'] >= date_low) & (df['timestamp'] <= date_high)][['timestamp','close','adjusted_close']]

def plot_month_data(df, month, year, ticker):
    '''
    Parameters
    ----------
    df : DataFrame
        the dataframe consisting of information from the month being plotted

    month : str
        the month of the year being plotted

    year : str
        the year the data is from

    ticker : str
        the stock ticker of the company which is being plotted.

    Returns
    -------
    a bokeh figure

    '''
    fig = figure(title=f'{ticker.upper()}', x_axis_label=f'{year}', y_axis_label="stock price ($)", sizing_mode="stretch_width")
    x = list(df['timestamp'].apply(lambda x: datetime.strptime(x,'%Y-%m-%d')))
    y1 = list(df['close'])
    y2 = list(df['adjusted_close'])
    
    fig.line(x, y1, legend_label="close", line_color="blue", line_width=4)
    fig.line(x, y2, legend_label="adjusted close", line_color="red", line_width=1)
    fig.xaxis[0].formatter = DatetimeTickFormatter(days="%b %d")
    return fig

    
st.write("This site is a simple app that makes a call to the Alpha Vantage API and plots \n"\
         +"a months worth of closing prices for a given stock. Have fun!")
         


#get the key to call AlphaVantage
API_KEY = os.environ['KEY']

#get the stock, month, and year
symbol = st.text_input('Enter a ticker (e.g. IBM)')
year = st.selectbox('Enter a year', ['']+sorted(range(2000,2022),reverse=True))
month = st.selectbox('Enter a month',['','Jan','Feb','Mar','Apr','May','Jun',\
                                       'Jul','Aug','Sep','Oct','Nov','Dec'])

#only move forward if the user has made the correct choices
if symbol != '' and year != '' and month != '':
    
    
    #build the query
    query = f'https://www.alphavantage.co/query?'+\
        f'function=TIME_SERIES_DAILY_ADJUSTED&'+\
        f'symbol={symbol}&'+\
        f'outputsize=full&'+\
        f'apikey={API_KEY}&'+\
        f'datatype=csv'

    #get the data
    df = get_df(query)

    #check if AlphaVantage returns an error. If no error, plot the month chosen
    if df.iloc[0,0].strip()[1:6]=='Error':
        st.write('not a valid ticker')
    else:
        month_df = get_month_data(df, month, year)
        fig = plot_month_data(month_df, month, year, symbol)
        st.bokeh_chart(fig, use_container_width=True)
