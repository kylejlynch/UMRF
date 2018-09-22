# -*- coding: utf-8 -*-
import pandas as pd
import sqlite3
import numpy as np
import imaplib, email
import os
import re
from bs4 import BeautifulSoup
import email
from datetime import date
import calendar
import string
from custom_functions import convtime, get_body, search
from sensitive import emailcredentials

def ticketsingle(yyyymmdd) :
    '''Gathers ticket data for a single day and separates by 30 min timeblock
        for use in Earnings_Time_Block.py
    '''
    conn = sqlite3.connect('UMRF_Incidents_SQL.sqlite')
    dfsql = pd.read_sql('''
                        SELECT *
                        FROM AllData
                        ''',conn)
    df = dfsql[dfsql['Date'] == yyyymmdd]
    df = df.filter(['opened_at','number'])
    df['opened_at'] = pd.to_datetime(df['opened_at'],infer_datetime_format=True)
    df = df.set_index('opened_at')
    df['count'] = 1
    dfcount = df['count'].resample('30T', label='right').sum()
    dfcount = dfcount.to_frame()
    if bool(re.search('07:00:00',dfcount.index.astype(str).tolist()[0])) : # in case agent opens ticket before 7am
        dfcount.iloc[1] += dfcount.iloc[0]
        dfcount = dfcount.drop(dfcount.index[0])
    if bool(re.search('20:30:00',dfcount.index.astype(str).tolist()[-1])) : # in case ticket is opened after 8pm
        dfcount.iloc[-2] += dfcount.iloc[-1]
        dfcount = dfcount.drop(dfcount.index[-1])
    dfcount = dfcount.rename_axis('Time Interval')
    return dfcount
    