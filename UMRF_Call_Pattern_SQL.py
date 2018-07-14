# -*- coding: utf-8 -*-
'''
Retrieves number of offered calls, accepted calls, and overflow (missed) calls for a single day
from data sent via email.
(for now saved files)
Used in UMRF_Earnings_Time_block.py
'''
import pandas as pd
import numpy as np
import imaplib, email
import os
import re
import sqlite3
from bs4 import BeautifulSoup
import email
from datetime import date
import calendar
import string
from custom_functions import convtime, get_body, search
from sensitive import emailcredentials

pd.set_option('display.max_columns', 100)

def callpatternsql() :
    conn = sqlite3.connect('UMRF_Call_Pattern.sqlite')
    dflist = []
    try :
        datelist = pd.read_sql_query('''SELECT DISTINCT "Date" FROM "AllData"''', conn)['Date'].tolist()
    except :
        datelist = []
    user, password, imap_url = emailcredentials()
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Call Pattern"')
    eml = search('Subject','FW: UMRF Calls Arrival Pattern for', mail)[0].split()
    #for i in eml[-7:] :
    for i in eml :
        result, data = mail.fetch(i,'(RFC822)')
        emlhtml = get_body(email.message_from_bytes(data[0][1]))   

        #extract data
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('for ([0-9-]+)', soup.text)[0]
        year, day, month = dt.split('-')
        day = calendar.day_name[calendar.weekday(int(year), int(day), int(month))]
        if dt not in datelist :
            print(dt,'not in')
            datelist.append(dt)
            #prep/clean data
            dfraw = pd.read_html(emlhtml,header=0)[0]
            dfraw = dfraw.iloc[14:40].reset_index(drop=True)
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
            df = dfraw.set_index('Time Interval').astype('int')
            df['Date'] = dt
            dflist.append(df)
        else :
            print(dt,'already in')
            continue
    if len(dflist) > 1 :
        dfall = pd.concat(dflist,axis=0).sort_values(by=['Date'],kind='mergesort')
        dfall.to_sql('AllData', conn, if_exists='append')
    elif len(dflist) == 1 :
        df.to_sql('AllData', conn, if_exists='append')
    elif len(dflist) == 0 :
        print('Already up to date!')
    conn.commit()
    conn.close()
callpatternsql()