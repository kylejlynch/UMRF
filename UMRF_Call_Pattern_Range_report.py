# -*- coding: utf-8 -*-
"""
Creates a report in Excel with Callflow averages and number of agent averages for a given period of time
"""
import pandas as pd
import numpy as np
import string
from UMRF_Number_Agents_Block import numberagentblock
from UMRF_Call_Pattern_Range import callpatternrange
from custom_functions import ampmtime
#from UMRF_Predict_Fit import nnfit
import calendar
from flask import request

def callrangeavg(start,end) :
    start = str(start)
    end = str(end)
    syear, smonth, sday  = start.split('-')
    eyear, emonth ,eday = end.split('-')
    smonth = calendar.month_name[int(smonth)]
    emonth = calendar.month_name[int(emonth)]
    
    exclude = [7356014,8569433,5806257,8661085]
    
    df1 = numberagentblock(start=start,end=end,exclude=exclude)
    df1 = df1.between_time('07:30:00','20:00:00')

    df2 = callpatternrange(start=start,end=end)
    df2.index = pd.to_datetime(df2.index)

    df = pd.concat([df2,df1], axis=1)
    df = df.reset_index(drop=True).set_index('Time Int').rename_axis('Time Interval')
    
    df = df.apply(pd.to_numeric, errors='ignore')
    dfavg = df.groupby(['rank','Day','Time Interval'],sort=False)['Calls Offered','Overflow Calls','number_agents'].mean()
    dfavg['Calls stdev'] = df.groupby(['rank','Day','Time Interval'],sort=False)['Calls Offered'].agg(np.std, ddof=0)
    dfavg['Overflow stdev'] = df.groupby(['rank','Day','Time Interval'],sort=False)['Overflow Calls'].agg(np.std, ddof=0)
    #dfavg['Pred Num Agents_avg'] = dfavg['Calls Offered']/1.32
    dfavg['Pred Num Agents_log'] = 24.265*np.log(0.0612*dfavg['Calls Offered'] - 0.08037*1 + 1.0359)
    #dfavg['Pred Num Agents_log'] = 20.8829*np.log(0.072*dfavg['Calls Offered'] - 0.0788*1 + 0.99769)
    #dfavg['Pred Num Agents_nn'] = dfavg['Calls Offered'].apply(lambda x : nnfit([x,1])[0])
    #dfavg['log_nn_avg'] = (dfavg['Pred Num Agents_log'] + dfavg['Pred Num Agents_nn'])/2
    #dfavg['diff'] = dfavg['log_nn_avg'] - dfavg['number_agents']
    dfavg['approx_agents_needed'] = dfavg['Pred Num Agents_log'] - dfavg['number_agents']
    dfavg = dfavg.round(3)
    
    dfavg = dfavg.apply(pd.to_numeric, errors='ignore')
    dfavg = dfavg.sort_index(level=0,sort_remaining=False).reset_index(level=0,drop=True)
    
    writer = pd.ExcelWriter('Avg_Callflow_{0}{1}to{2}{3}.xlsx'.format(smonth,sday,emonth,eday))
    dfavg.to_excel(writer,'Sheet1')
    worksheet = writer.sheets['Sheet1']
    letters = list(string.ascii_uppercase)
    for i,col in enumerate(list(dfavg.reset_index())) :    #autofit column-width
        worksheet.set_column('{}:{}'.format(letters[i],letters[i]), max(12,len('{}'.format(col))+2,dfavg.reset_index()['{}'.format(col)].astype(str).map(len).max()+2))
    return writer.save()
callrangeavg('2018-07-01','2018-07-27')