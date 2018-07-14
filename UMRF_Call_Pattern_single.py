# -*- coding: utf-8 -*-
'''
Retrieves number of offered calls, accepted calls, and overflow (missed) calls for a single day
from saved files.
callpatternsing requires input 'yyyymmdd', where dt is a date in yyyy-mm-dd format
Used in UMRF_Earnings_Time_block.py
'''
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

pd.set_option('display.max_columns', 100)

def callpatternsing(yyyymmdd) :
    conn = sqlite3.connect('UMRF_Call_Pattern.sqlite')
    dfsql = pd.read_sql('''
                        SELECT *
                        FROM AllData
                        ''',conn)
    df = dfsql[dfsql['Date'] == yyyymmdd]
    time = pd.date_range(start='{} 07:30:00'.format(yyyymmdd),end = '{} 20:00:00'.format(yyyymmdd),freq='30T')
    df = df.set_index(time)
    return df
