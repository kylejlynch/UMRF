# -*- coding: utf-8 -*-
import requests
import json
import sqlite3
import pandas as pd
import string
import numpy as np
import string
from matplotlib import pyplot as plt
from sensitive import wheniworktoken
from custom_functions import convtime

'''
Predicts labor cost based on schedules. Breaks the schedules into 30 min time blocks.
This will be used to compare scheduled vs actual hours. It will incorporate hourly pay from
SQL database emplist.sqlite to yield predicted labor cost per 30 min time block.

It will compare predicted number of agents to actual agents and compare with the number of overflow calls
for schedule optimization

32290124 = openshift?
'''

### List shifts on date(s)
pd.set_option('display.max_columns', 100)

headers = wheniworktoken()
params = (
    ('location_id', '2875441'),
    ('start', '2018-08-02'),
    ('end', '2018-08-26')
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
'''
conn = sqlite3.connect('emplist.sqlite')
dfemp = pd.read_sql('SELECT * FROM info',conn)
dfemp = dfemp.rename(columns={'id':'user_id'})
dfemp = dfemp.filter(['user_id','first_name','last_name'])
'''
dfdata = dfraw.filter(['user_id','position_id','start_time','end_time'])
dfdata = dfdata[~(dfdata['position_id'] == 7356014)].drop(columns=['position_id'])
dfdata['date'] = dfdata['start_time'].str.extract('(..\s...\s....)')
dfdata['date'] = pd.to_datetime(dfdata['date'], infer_datetime_format=True).dt.date
dfdata['s_time'] = dfdata['start_time'].str.extract('(..:..:..)')
dfdata['s_time'] = dfdata['s_time'].apply(lambda x : float(convtime(x)[0]))
dfdata['e_time'] = dfdata['end_time'].str.extract('(..:..:..)')
dfdata['e_time'] = dfdata['e_time'].apply(lambda x : float(convtime(x)[0]))
'''
dfmerge = pd.merge(dfraw,dfemp,on='user_id')
dfmerge = dfmerge.filter(['first_name','last_name','start_time','end_time','creator_id'])
dfmerge = dfmerge[dfmerge['first_name'] == 'Alia']
print(dfmerge)
'''

rng_lst = []
for i,j in zip(dfdata['s_time'].tolist(),dfdata['e_time'].tolist()):
    rng_lst.append(np.arange(round(i*2)/2,j,0.5).tolist())
rnglst = [y for x in rng_lst for y in x]

bins = np.arange(7.0, 21.0,0.5) - 0.25
fig, ax = plt.subplots()
xaxis = ['7:30AM','8:00AM','8:30AM','9:00AM',
         '9:30AM','10:00AM','10:30AM','11:00AM','11:30AM',
         '12:00PM','12:30PM','1:00PM','1:30PM','2:00PM',
         '2:30PM','3:00PM','3:30PM','4:00PM','4:30PM',
         '5:00PM','5:30PM','6:00PM','6:30PM','7:00PM',
         '7:30PM','8:00PM']
plt.hist(rnglst,bins=bins,alpha=0.5,rwidth=0.8)
ax.set_xticks(np.arange(7,20,0.5))
ax.set_xticklabels(xaxis,rotation=60)
plt.subplots_adjust(bottom=0.25)

"""
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
"""