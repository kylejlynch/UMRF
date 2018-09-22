# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 10:44:40 2018

@author: Labuser
"""
import imaplib, email
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import re
import calendar
from sensitive import emailcredentials
from custom_functions import get_body,search,get_emails,convtime
from io import StringIO
from datetime import date,datetime,timedelta
'''
text = '11:30A M'
df = pd.DataFrame({'Time':[text]})
print(df)
dfr = df.replace({'A\sM':'AM'},regex=True)
print(dfr)

try :
    h = open('file.txt')
except :
    print('could not read')
try :
    h = open('hey.txt')
except :
    print('hi')
'''
'''
days = {'Monday':int(0), 'Tuesday':int(1), 'Wednesday':int(2), 'Thursday':int(3), 'Friday':int(4), 'Saturday':int(5), 'Sunday':int(6)}
user, password, imap_url = emailcredentials()
mail = imaplib.IMAP4_SSL(imap_url)
mail.login(user,password)
mail.select('"Call Pattern"')
eml = search('ON', "23-Aug-2018", mail)[0].split()
for i in eml[-1:] :
#for i in eml :
    result, data = mail.fetch(i,'(RFC822)')
    emlhtml = get_body(email.message_from_bytes(data[0][1]))   

    #extract data
    soup = BeautifulSoup(emlhtml, 'lxml')
    dt = re.findall('for ([0-9-]+)', soup.text)[0]
    year, month, day = dt.split('-')
    day = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
    #prep/clean data
    dfraw = pd.read_html(emlhtml,header=0)[0]
    dfraw = dfraw.iloc[14:40].reset_index(drop=True)
    dfraw.replace({'! ':'','!':'','< /td>':'','<tr>':'','< td>':'','< tr>':'','A\sM':'AM','[0-9]+\s':''}, regex=True,inplace=True)
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
    print(df)
'''
today = datetime.strftime(datetime.today(), '%Y-%m-%d')
yest = datetime.strftime(datetime.strptime(today,'%Y-%m-%d').date(),'%Y-%m-%d')
today = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(2)).strftime('%Y-%m-%d')
lstwk = datetime.strftime(datetime.now() - timedelta(8), '%Y-%m-%d')
print(yesterday)