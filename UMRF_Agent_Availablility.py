# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 22:55:51 2018

@author: Kyle
"""

import numpy as np
from sensitive import wheniworktoken
import pandas as pd
import requests
import sqlite3

pd.set_option('display.max_columns', 100)

headers = wheniworktoken()
'''
r = requests.get('https://api.wheniwork.com/2/availabilities', headers=headers)
j = r.json()
j = j["availabilities"]

data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue

df = pd.DataFrame(data)
print(df)
'''

r = requests.get('https://api.wheniwork.com/2/availabilities/items', headers=headers)
j = r.json()
j = j["availabilityitems"]

data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue

df = pd.DataFrame(data)

conn = sqlite3.connect('emplist.sqlite')
dfemp = pd.read_sql('SELECT * FROM info',conn)
dfemp = dfemp.rename(columns={'id':'user_id'})
dfemp = dfemp.filter(['user_id','first_name','last_name'])
dfmerge = pd.merge(df,dfemp,on='user_id')
dfmerge = dfmerge.filter(['first_name','last_name','start_time','end_time','day','type','start_date','end_date','created_at','updated_at'])
dfmerge['updated_at'] = dfmerge['updated_at'].str.extract('(..\s...\s....\s..:..:..)')
dfmerge['created_at'] = dfmerge['created_at'].str.extract('(..\s...\s....\s..:..:..)')
dfmerge['start_date'] = dfmerge['start_date'].str.extract('...,\s(..\s...\s....)')
dfmerge['end_date'] = dfmerge['end_date'].str.extract('...,\s(..\s...\s....)')
dfmerge['updated_at'] = pd.to_datetime(dfmerge['updated_at'],infer_datetime_format=True)
dfmerge['created_at'] = pd.to_datetime(dfmerge['created_at'],infer_datetime_format=True)
dfmerge['start_date'] = pd.to_datetime(dfmerge['start_date'],infer_datetime_format=True)
dfmerge['end_date'] = pd.to_datetime(dfmerge['end_date'],infer_datetime_format=True)
dayOfWeek={0:'Sunday',1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday'}
type={1:'Unavailable', 2:'Preferred'}
dfmerge['day'] = dfmerge['day'].map(dayOfWeek)
dfmerge['type'] = dfmerge['type'].map(type)
print(dfmerge)

conn = sqlite3.connect('availability.sqlite')
dfmerge.to_sql('info', conn,if_exists='replace',index=False)

conn.commit()
conn.close()
