# -*- coding: utf-8 -*-
"""
Plots call overflow,accepted calls, and number of agents for in 30min time blocks for the previous day.
Uses UMRF_Call_Pattern_single.py
Uses UMRF_Earnings_Time_Block.py
"""
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from datetime import date
import calendar
import matplotlib.pyplot as plt
from custom_functions import ampmtime
from UMRF_Call_Pattern_single import callpatternsing
from UMRF_Earnings_Time_Block import workedshiftblock

def overflowagent(yyyymmdd=None) :
    if yyyymmdd is None :
        start = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    else :
        start = yyyymmdd
    end_plus1 = datetime.strftime(datetime.strptime(start,'%Y-%m-%d') + timedelta(1), '%Y-%m-%d')
    
    dfraw = callpatternsing(start)

    df_call = dfraw.filter(['Overflow Calls'])

    dfdata = workedshiftblock(start,exclude=[7356014,8569433,5806257])[1]

    hour_list = []
    for index,row in dfdata.iterrows() :
        time = pd.date_range(start=row['start_time'], end=row['end_time'],freq='S')
        s = pd.Series(0.00027778,index=time,name='hours')
        s = s.resample('30T',label='right',closed='right').sum()
        hour_list.append(s)
        
    dftemp2 = pd.concat(hour_list,axis=1)
    dftemp2['number_agents'] = (dftemp2.sum(axis=1))*2 # Number of hours = number of agents
    df = dftemp2['number_agents']
    
    df_final = pd.concat([df,df_call], axis=1).fillna(0) # concats and fills opening and closing time blocks
    
    year, month, day = start.split('-')
    dayname = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
    month = calendar.month_name[int(month)]

    df_final['number_agents'].plot.bar(alpha=0.60,color='blue',width=0.85,legend=True)
    df_final['Overflow Calls'].plot.bar(alpha=0.80,color='red',width=0.50,legend=True)
    plt.subplots_adjust(bottom=0.25)
    plt.xlabel('Time')
    plt.ylabel('Overflow Calls/Num. of Agents')
    plt.title('Overflow and Agent Count for {0},\n{1} {2}, {3}'.format(dayname,month,day,year))
    ticks = (df_final.reset_index()['index'].dt.time).apply(lambda x : ampmtime(x))
    plt.xticks(np.arange(len(df_final.index)),ticks,rotation=75)
    ax = plt.gca()
    ax.legend(['Number of Agents','Overflow Calls'])
    plt.savefig('overflowagent_yesterday.png',bbox_inches='tight')
overflowagent('2018-09-17')