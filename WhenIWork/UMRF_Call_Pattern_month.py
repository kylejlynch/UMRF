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
'''
Retrieves number of offered calls, accepted calls, and overflow (missed) calls over a given period
and averages them per 30 min time block. Also calculates the standard deviation for both accepted and overflow calls.
Predicts the minimum number of  agents needed to accept all calls (minimize overflow calls as well as labor cost)
based on previous month.
'''

pd.set_option('display.max_columns', 100)

def callpattern() :
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
            dfraw = dfraw.reset_index()
            dfraw['Day'] = day
            df = df.append(dfraw)
        else : continue
    df['rank'] = df['Day'].map(days)
    df = df.apply(pd.to_numeric, errors='ignore')
    dfavg = df.groupby(['rank','Day','Time Interval'],sort=False)['Calls Offered','Overflow Calls'].mean()
    dfavg['Calls stdev'] = df.groupby(['rank','Day','Time Interval'],sort=False)['Calls Offered'].agg(np.std, ddof=0)
    dfavg['Overflow stdev'] = df.groupby(['rank','Day','Time Interval'],sort=False)['Overflow Calls'].agg(np.std, ddof=0)
    dfavg['Pred Num Agents'] = dfavg['Calls Offered']/1.32
    dfavg = dfavg.round(3)
    
    dfavg = dfavg.apply(pd.to_numeric, errors='ignore')
    dfavg = dfavg.sort_index(level=0,sort_remaining=False).reset_index(level=0,drop=True)
    
    writer = pd.ExcelWriter('Avg_Callflow.xlsx')
    dfavg.to_excel(writer,'Sheet1')
    worksheet = writer.sheets['Sheet1']
    letters = list(string.ascii_uppercase)
    for i,col in enumerate(list(dfavg.reset_index())) :    #autofit column-width
        worksheet.set_column('{}:{}'.format(letters[i],letters[i]), max(12,len('{}'.format(col))+2,dfavg.reset_index()['{}'.format(col)].astype(str).map(len).max()+2))
    return writer.save()
callpattern()