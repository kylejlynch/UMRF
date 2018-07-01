# -*- coding: utf-8 -*-
import requests
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import string
from sensitive import wheniworktoken

'''
Retrieves start/end times of worked shifts, shift lengths, hourly rates for dates selected and calculates labor cost.
Retrieves incidents created for each day and calculates earnings from revenue (subtracts labor cost).
Generates Excel report of earnings per day for given time period.
'''
pd.set_option('display.max_columns', 100)

### Labor cost/calls needed
start='2018-03-26'
end='2018-06-15'
end_plus1 = datetime.strftime(datetime.strptime(end,'%Y-%m-%d') + timedelta(1), '%Y-%m-%d')

headers = wheniworktoken()
params = (
    ('start', start),
    ('end', end_plus1),
)

r = requests.get('https://api.wheniwork.com/2/times', headers=headers, params=params)
j = r.json()
j = j['times']
data = {k:[] for k,v in j[0].items()}
for i in j :
    for k,v in i.items():
        try :
            data[k].append(v)
        except : continue
dfraw = pd.DataFrame(data)
dfdata = dfraw.filter(['user_id','position_id','start_time','end_time','length','hourly_rate','notes'])
dfdata = dfdata[~(dfdata['position_id'] == 7356014)].drop(columns=['position_id'])
dfdata['date'] = dfdata['start_time'].str.extract('(..\s...\s....)')
dfdata['date'] = pd.to_datetime(dfdata['date'], infer_datetime_format=True).dt.date

dflist = []
for date in dfdata['date'].unique() :
    dfgroup = dfdata[dfdata['date'] == date]
    cost = sum(dfgroup['length']*dfgroup['hourly_rate'])
    costp = cost*1.20
    callsl = cost/13.80
    calls = costp/13.80
    df = pd.DataFrame({'Date' : [date],
                       'labor_cost' : [cost], 
                       'labor_plus_20' : [costp], 
                       'calls_needed_labor' : [callsl], 
                       'calls_needed_20' : [calls]})
    dflist.append(df)

dftemp = pd.concat(dflist).reset_index(drop=True)
dftemp['Date'] = dftemp['Date'].astype(str)

conn = sqlite3.connect('UMRF_SQL_Daily.sqlite')
dfsql = pd.read_sql('''SELECT Date, sum(IncidentsCreated) AS IncidentsCreated
                      FROM AllData
                      WHERE Date BETWEEN "{0}" AND "{1}"
                      GROUP BY Date'''.format(start,end),conn)

df = pd.merge(dftemp,dfsql, on='Date')
df['Revenue'] = df['IncidentsCreated']*13.80
df['Earn_aft_labor'] = df['Revenue'] - df['labor_cost']
df['Earn_aft_20'] = df['Revenue'] - df['labor_plus_20']

letters = list(string.ascii_uppercase)
writer = pd.ExcelWriter('earnings.xlsx')
df.to_excel(writer,'Sheet1')
worksheet = writer.sheets['Sheet1']
for i,col in enumerate(list(df)) :    #autofit column-width
    worksheet.set_column('{}:{}'.format(letters[i+1],letters[i+1]), max(len('{}'.format(col))+2,df['{}'.format(col)].astype(str).map(len).max()+2))
writer.save()
