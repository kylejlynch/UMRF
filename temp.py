# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
import numpy as np
import email
from bs4 import BeautifulSoup
from datetime import date
import calendar
import requests
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from sensitive import wheniworktoken
from custom_functions import ampmtime
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from sklearn.svm import SVR
from sklearn import linear_model
import matplotlib.pyplot as plt
'''
df = pd.DataFrame({'hey' : [1,2,3],'hi' : [1,pd.NaT,3]})

print(df['hi'].replace(pd.NaT,'time'))

print(pd.date_range(start='2018-01-01 07:00:00', end='2018-02-01 20:00:00', freq='30T').astype('str'))

print(np.sort(5 * np.random.rand(40, 1)))
'''
df = pd.DataFrame()
datelist = []
for root, dirs, files in os.walk('Call Patterns/') :
    for file in files :
        print(file)
        fh = open(os.path.join(root, file), "rb")
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
            dfraw = dfraw.reset_index(drop=True)
            dfraw['Day'] = day
            dfraw = dfraw.reset_index(drop=True)
            dfraw['Time Interval'] = pd.date_range(start='{} 07:30:00'.format(dt), end='{} 20:00:00'.format(dt), freq='30T').astype('str')
            dfraw = dfraw.set_index(['Time Interval'])
            dfraw['Percent_ACD'] = (dfraw['ACD Calls'].astype('int')/dfraw['Calls Offered'].astype('int')).replace([np.inf,-np.inf],np.nan).fillna(0)
            df = df.append(dfraw)
        else : continue
df_call = df.apply(pd.to_numeric, errors='ignore')
print(df_call)
