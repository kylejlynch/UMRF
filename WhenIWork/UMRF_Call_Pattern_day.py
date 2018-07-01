# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import re
from bs4 import BeautifulSoup
import email
from datetime import date
import calendar
import string
from custom_functions import convtime
from sensitive import emailcredentials
'''
Retrieves number of offered calls, accepted calls, and overflow (missed) calls for a single day
from data sent via email.
(for now saved files)
Used in UMRF_Earnings_Time_block.py
'''

pd.set_option('display.max_columns', 100)

#user, password, imap_url = emailcredentials

def callpattern(date) :
    df = pd.DataFrame()
    datelist = []
    days = {'Monday':int(0), 'Tuesday':int(1), 'Wednesday':int(2), 'Thursday':int(3), 'Friday':int(4), 'Saturday':int(5), 'Sunday':int(6)}
    
    path = 'Call Patterns/June2018/'
    listing = os.listdir(path)
    for file in listing :
        fh = open(os.path.join(path,file), 'rb')
        handle = email.message_from_string(fh.read().decode())
        if handle.is_multipart() :
            for part in handle.walk() :
                if part.get_content_type() == 'text/html' :
                    try :
                        emlhtml = part.get_payload(decode=True).decode()
                    except :
                        emlhtml = part.get_payload(decode=True).decode(encoding='cp1252')
        else :
            emlhtml = handle.get_payload()
        
        #extract data
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('for ([0-9-]+)', soup.text)[0]
        year, day, month = dt.split('-')
        day = calendar.day_name[calendar.weekday(int(year), int(day), int(month))]
        if dt not in datelist :
            datelist.append(dt)
        
            #prep/clean data
            dfraw = pd.read_html(emlhtml,header=0)[0]
            dfraw = dfraw.iloc[14:40].reset_index()
            dfraw.replace({'! ':'','!':'','< /td>':'','<tr>':'','< td>':'','< tr>':''}, regex=True,inplace=True)
            if not 'Overflow Calls' in dfraw :
                dfraw['Overflow Calls'] = dfraw['Calls Offered'].astype('float') - dfraw['ACD Calls'].astype('float')
                
            if dfraw['Overflow Calls'].isnull().values.any() :
                nanindex = dfraw[dfraw.isnull().any(axis=1)]
                for i in nanindex.index.values :
                    dfraw1 = dfraw[['Time Interval']]
                    dfraw2 = dfraw[['SL Abandoned','Abandoned Calls','Calls Offered','ACD Calls','Overflow Calls']]
                    dfraw2.iloc[i] = dfraw2.iloc[i].shift(1)
                    dfraw = pd.concat([dfraw1,dfraw2],axis=1,sort=False)
                    dfraw['SL Abandoned'] = dfraw['SL Abandoned'].fillna(0)
            #dfraw = dfraw.drop(columns=['index'])
            dfraw = dfraw.set_index('Time Interval')
            dfraw['Date'] = dt
            df = df.append(dfraw)
        else : continue
    df = df[df['Date'] == date]
    time = pd.date_range(start='{} 07:30:00'.format(date),end = '{} 20:00:00'.format(date),freq='30T')
    df = df.set_index(time)
    return df