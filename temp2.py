# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import re
from bs4 import BeautifulSoup
import email
from datetime import date
import calendar

pd.set_option('display.max_columns', 100)

df = pd.DataFrame()
datelist = []

path = 'Call Patterns/May2018/'
file = 'noname_9.eml'

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
        print(dt,file)
        nanindex = dfraw[dfraw.isnull().any(axis=1)]
        for i in nanindex.index.values :
            print(i,nanindex.index.values)
            dfraw1 = dfraw[['Time Interval']]
            dfraw2 = dfraw[['SL Abandoned','Abandoned Calls','Calls Offered','ACD Calls','Overflow Calls']]
            dfraw2.iloc[i] = dfraw2.iloc[i].shift(1)
            dfraw = pd.concat([dfraw1,dfraw2],axis=1,sort=False)
            dfraw['SL Abandoned'] = dfraw['SL Abandoned'].fillna(0)

    #dfraw = dfraw.set_index('Time Interval')
    #dfraw['Overflow Calls'] = dfraw['Overflow Calls'].astype('str').replace({'[^0-9.]*':''}, regex=True)
    #dfraw = dfraw.reset_index()
    dfraw['Day'] = day
    df = df.append(dfraw)

df = df.apply(pd.to_numeric, errors='ignore')
dfavg = df.groupby(['Day','Time Interval'],sort=False)['Calls Offered'].mean().round(2)
print(dfavg)
