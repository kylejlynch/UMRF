# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import re
from bs4 import BeautifulSoup
import calendar
import email
import matplotlib.pyplot as plt
from custom_functions import ampmtime
from UMRF_Earnings_Time_Block import workedshiftblock
'''
Retrieves number of offered calls, accepted calls, and overflow (missed) calls for a single day
from saved files.
'''

pd.set_option('display.max_columns', 100)

def callpattern(yyyymmdd) :
    start = yyyymmdd
    df = pd.DataFrame()
    datelist = []

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
            dfraw = dfraw.set_index('Time Interval')
            dfraw['Date'] = dt
            df = df.append(dfraw)
        else : continue
    df = df[df['Date'] == start]
    time = pd.date_range(start='{} 07:30:00'.format(start),end = '{} 20:00:00'.format(start),freq='30T')
    df = df.set_index(time)
    return start, df

start, df_call = callpattern('2018-06-03')

dfdata = workedshiftblock(start,exclude=[7356014])[1]

start, dfdata = workedshiftblock(yyyymmdd=start)
labor_list = []
hour_list = []
for index,row in dfdata.iterrows() :
    time = pd.date_range(start=row['start_time'], end=row['end_time'],freq='S')
    s = pd.Series(0.0002778,index=time,name='hours')
    s = s.resample('30T',label='right',closed='right').sum()
    hour_list.append(s)
    s = s*row['hourly_rate']
    labor_list.append(s)
    
dftemp1 = pd.concat(labor_list,axis=1)
dftemp2 = pd.concat(hour_list,axis=1)
dftemp1['labor_cost'] = dftemp1.sum(axis=1) # Cost of labor per 30 min block
dftemp2['hour_cost'] = dftemp2.sum(axis=1) # Number of hours worked per 30 min block
df = dftemp1['labor_cost']

df_call['ACD_calls_revenue'] = df_call['ACD Calls'].astype(int)*float(13.80)
df_final = pd.concat([df, df_call['ACD_calls_revenue']], axis=1).fillna(0)
df_final['earnings'] = df_final['ACD_calls_revenue'] - df_final['labor_cost']

year, month, day = start.split('-')
dayname = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
month = calendar.month_name[int(month)]

df_final['ACD_calls_revenue'].plot.bar(alpha=0.60,color='green',width=0.85,legend=True)
df_final['labor_cost'].plot.bar(alpha=0.60,color='red',width=0.50,legend=True)
plt.subplots_adjust(bottom=0.25)
plt.xlabel('Time')
plt.ylabel('Revenue/Labor ($)')
plt.title('Labor and Revenue for {0},\n{1} {2}, {3}'.format(dayname,month,day,year))
ticks = (df_final.reset_index()['index'].dt.time).apply(lambda x : ampmtime(x))
plt.xticks(np.arange(len(df_final.index)),ticks,rotation=75)
ax = plt.gca()
ax.legend(['Calls Revenue', 'Labor Cost'])
plt.savefig('timeblock_{}{}{}.png'.format(year,month,day),bbox_inches='tight')