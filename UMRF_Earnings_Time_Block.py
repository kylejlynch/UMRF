# -*- coding: utf-8 -*-
'''
Retreives shift information (start, end times),hourly rate and breaks the shifts into 30 min
blocks of time to calculate a total labor cost per 30 min block of the workday.
Finally the call flow (number of calls per 30 min block) from UMRF_Call_Pattern_single.py is imported to
generate the earnings for each 30 min time block of the 
Uses UMRF_Call_Pattern_single.py
'''
import pandas as pd
import numpy as np
import requests
from datetime import datetime,timedelta
import calendar
import math
import matplotlib.pyplot as plt
from custom_functions import convtime
from sensitive import wheniworktoken
from custom_functions import ampmtime
from UMRF_Call_Pattern_single import callpatternsing

pd.set_option('display.max_columns', 100)

def workedshiftblock(start=None,end=None,exclude=None) :
    if start is None :
        start = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    else :
        start = start
    if end is None :
        end_plus1 = datetime.strftime(datetime.strptime(start,'%Y-%m-%d') + timedelta(1), '%Y-%m-%d')
    else :
        end_plus1 = datetime.strftime(datetime.strptime(end,'%Y-%m-%d') + timedelta(1), '%Y-%m-%d')
    if exclude is None :
        exclude_list = [7356014]
    else :
        exclude_list = exclude
    
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
    dfdata = dfdata[~(dfdata['position_id'].isin(exclude_list))].drop(columns=['position_id'])
    dfdata['start_time'] = dfdata['start_time'].str.extract('(..\s...\s....\s..:..:..)')
    dfdata['start_time'] = pd.to_datetime(dfdata['start_time'],infer_datetime_format=True)
    dfdata['end_time'] = dfdata['end_time'].str.extract('(..\s...\s....\s..:..:..)')
    dfdata['end_time'] = dfdata['end_time'].replace(pd.NaT,'{} 20:00:00'.format(start)) # in case someone forgets to clock out at 8pm
    dfdata['end_time'] = pd.to_datetime(dfdata['end_time'],infer_datetime_format=True)
    return start, dfdata

def earntimeblock() :
    start, dfdata = workedshiftblock()
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
    
    df_call = callpatternsing(start)
    
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
    plt.savefig('timeblock_yesterday.png',bbox_inches='tight')
    plt.close('all')