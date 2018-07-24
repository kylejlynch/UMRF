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

def callpatternfile() :
    conn = sqlite3.connect('UMRF_Call_Pattern.sqlite')
    days = {'Monday':int(0), 'Tuesday':int(1), 'Wednesday':int(2), 'Thursday':int(3), 'Friday':int(4), 'Saturday':int(5), 'Sunday':int(6)}
    dflist = []
    try :
        datelist = pd.read_sql_query('''SELECT DISTINCT "Date" FROM "AllData"''', conn)['Date'].tolist()
    except :
        datelist = []
    for root, dirs, files in os.walk('Call Patterns/') :
        for file in files :
            fh = open(os.path.join(root,file), 'rb')
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
            year, month, day = dt.split('-')
            day = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
            if dt not in datelist :
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
                dfraw['Day'] = day
                dfraw = dfraw.reset_index()
                dfraw = dfraw.rename(columns={'Time Interval': 'Time Int'})
                dfraw['Time Interval'] = pd.date_range(start='{} 07:30:00'.format(dt), end='{} 20:00:00'.format(dt), freq='30T').astype('str')
                df = dfraw.set_index(['Time Interval'])
                df = df.drop(columns=['index'])
                df['Date'] = dt
                df['rank'] = df['Day'].map(days)
                dflist.append(df)
            else : continue
    try :
        df_call = pd.concat(dflist,axis=0).sort_values(by=['Date'],kind='mergesort')
        df_call = df_call.apply(pd.to_numeric, errors='ignore')
        df_call.to_sql('AllData', conn, if_exists='append')
        conn.commit()
        conn.close()
    except : print('No files to add!')

def callpatternsql() :
    conn = sqlite3.connect('UMRF_Call_Pattern.sqlite')
    dflist = []
    days = {'Monday':int(0), 'Tuesday':int(1), 'Wednesday':int(2), 'Thursday':int(3), 'Friday':int(4), 'Saturday':int(5), 'Sunday':int(6)}
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
            dfraw['Day'] = day
            dfraw = dfraw.reset_index()
            dfraw = dfraw.rename(columns={'Time Interval': 'Time Int'})
            dfraw['Time Interval'] = pd.date_range(start='{} 07:30:00'.format(dt), end='{} 20:00:00'.format(dt), freq='30T').astype('str')
            df = dfraw.set_index(['Time Interval'])
            df = df.drop(columns=['index'])
            df['Date'] = dt
            df['rank'] = df['Day'].map(days)
            dflist.append(df)
        else :
            print(dt,'already in')
            continue
    if len(dflist) > 1 :
        dfall = pd.concat(dflist,axis=0).sort_values(by=['Date'],kind='mergesort')
        dfall = dfall.apply(pd.to_numeric, errors='ignore')
        dfall.to_sql('AllData', conn, if_exists='append')
    elif len(dflist) == 1 :
        df = df.apply(pd.to_numeric, errors='ignore')
        df.to_sql('AllData', conn, if_exists='append')
    elif len(dflist) == 0 :
        print('Already up to date!')
    conn.commit()
    conn.close()
callpatternfile()
callpatternsql()