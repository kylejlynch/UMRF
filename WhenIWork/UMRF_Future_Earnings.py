# -*- coding: utf-8 -*-
import requests
import json
import sqlite3
import pandas as pd
import string
import numpy as np
import re
import string
from sensitive import wheniworktoken

'''
Furture Earninings
Predicts how many calls are needed per day to cover labor costs as well as labor + 20%
for a given time period.

32290124 = openshift?
'''

pd.set_option('display.max_columns', 100)

def convtime(t) :
    h,m,s = re.split(':',t)
    _hrs = int(h) + int(m)/60 + int(s)/3600
    _min = int(h)*60 + int(m) + int(s)/60
    return '{:.3f}'.format(_hrs),'{:.3f}'.format(_min)

headers = wheniworktoken()
params = (
    ('location_id', '2875441'),
    ('start', '2018-06-22'),
    ('end', '2018-06-30')
)

r = requests.get('https://api.wheniwork.com/2/shifts/', headers=headers, params=params)
j = r.json()
j = j['shifts']

data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue
dfraw = pd.DataFrame(data)
print(dfraw)
dfdata = dfraw.filter(['user_id','position_id','start_time','end_time'])
dfdata = dfdata[~(dfdata['position_id'] == 7356014)].drop(columns=['position_id'])
dfdata['date'] = dfdata['start_time'].str.extract('(..\s...\s....)')
dfdata['date'] = pd.to_datetime(dfdata['date'], infer_datetime_format=True).dt.date
dfdata['s_time'] = dfdata['start_time'].str.extract('(..:..:..)')
dfdata['s_time'] = dfdata['s_time'].apply(lambda x : float(convtime(x)[0]))
dfdata['e_time'] = dfdata['end_time'].str.extract('(..:..:..)')
dfdata['e_time'] = dfdata['e_time'].apply(lambda x : float(convtime(x)[0]))
dfdata['length'] = dfdata['e_time'] - dfdata['s_time']

conn = sqlite3.connect('emplist.sqlite')
dfsql = pd.read_sql('''SELECT id AS user_id, 
                        hourly_rate
                        FROM info''', conn)
dfdata = pd.merge(dfdata, dfsql, on='user_id')

dflist = []
for date in dfdata['date'].unique() :
    dfgroup = dfdata[dfdata['date'] == date]
    cost = sum(dfgroup['length']*dfgroup['hourly_rate'])
    hours = sum(dfgroup['length'])
    costp = cost*1.20
    callsl = cost/13.80
    calls = costp/13.80
    df = pd.DataFrame({'Date' : [date],
                       'total_hours' : [hours],
                       'labor_cost' : [cost],
                       'labor_plus_20' : [costp], 
                       'calls_needed_labor' : [callsl], 
                       'calls_needed_20' : [calls]})
    dflist.append(df)
df = pd.concat(dflist).reset_index(drop=True)
df = df.sort_values(by='Date').reset_index(drop=True)
print(df)

conn.commit()
conn.close()

letters = list(string.ascii_uppercase)
writer = pd.ExcelWriter('future_earnings.xlsx')
df.to_excel(writer,'Sheet1')
worksheet = writer.sheets['Sheet1']
for i,col in enumerate(list(df)) :    #autofit column-width
    worksheet.set_column('{}:{}'.format(letters[i+1],letters[i+1]), max(len(col)+2,df['{}'.format(col)].astype(str).map(len).max()+2))
writer.save()