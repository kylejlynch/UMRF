# -*- coding: utf-8 -*-
"""
Sums and produces a pd series with number of agents in 30 min time blocks for a given period
Uses workedshiftblock from UMRF_Earnings_Time_Block.py
"""
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from UMRF_Earnings_Time_Block import workedshiftblock


def numberagentblock(start=None,end=None,exclude=None) :
    if start is None :
        start = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    else :
        start = start
        end = end
    if end is None :
        end = end
    else :
        end = end
    if exclude is None :
        exclude_list = [7356014]
    else :
        exclude_list = exclude

    dfdata = workedshiftblock(start=start,end=end,exclude=exclude_list)[1]

    hour_list = []
    for index,row in dfdata.iterrows() :
        time = pd.date_range(start=row['start_time'], end=row['end_time'],freq='S')
        s = pd.Series(0.00027778,index=time,name='hours')
        s = s.resample('30T',label='right',closed='right').sum()
        s = s.to_frame().rename_axis('Time Interval')
        hour_list.append(s)
        
    dftemp2 = pd.concat(hour_list,axis=1)
    dftemp2['number_agents'] = (dftemp2.sum(axis=1))*2 # Number of hours = number of agents
    df = dftemp2['number_agents']
    return df

#df = numberagentblock(start='2018-07-01',end='2018-07-02',exclude = [7356014,8569433,5806257])
