# -*- coding: utf-8 -*-
"""
1. Retrieves number of offered calls, accepted calls, and overflow (missed) calls over a given period
2. Retrieves start/end times for agents each day in given time period
3. Calculates an equation that predicts the minimum number of agents needed to accept all calls to take call flow based on data in the
    given time period using Scipy to try vaious fits
4. Produces 3d plot for visualization of the fit
"""
import pandas as pd
import numpy as np
import os
import re
from bs4 import BeautifulSoup
import email
from datetime import date
import calendar
import requests
from datetime import datetime,timedelta
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from sensitive import wheniworktoken
from UMRF_Call_Pattern_Range import callpatternrange
from custom_functions import ampmtime
from matplotlib import cm
from scipy.optimize import curve_fit
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from scipy import stats

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 300)

def timeblockrange(start,end,exclude=None) :
    start = start
    end = end
    if exclude is None :
        exclude_list = [7356014]
    else :
        exclude_list = exclude
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
    dfdata = dfdata[~(dfdata['position_id'].isin(exclude_list))].drop(columns=['position_id'])
    dfdata['start_time'] = dfdata['start_time'].str.extract('(..\s...\s....\s..:..:..)')
    dfdata['start_time'] = pd.to_datetime(dfdata['start_time'],infer_datetime_format=True)
    dfdata['end_time'] = dfdata['end_time'].str.extract('(..\s...\s....\s..:..:..)')
    dfdata['end_time'] = dfdata['end_time'].replace(pd.NaT,'{} 20:00:00'.format(start)) # in case someone forgets to clock out at 8pm
    dfdata['end_time'] = pd.to_datetime(dfdata['end_time'],infer_datetime_format=True)
    dfdata['Date'] = dfdata['end_time'].astype('str').str.extract('(....-..-..)')

    hour_list = []
    for index,row in dfdata.iterrows() :
        time = pd.date_range(start=row['start_time'], end=row['end_time'],freq='S')
        s = pd.Series(0.00027778,index=time,name='hours')
        s = s.resample('30T',label='right',closed='right').sum()
        hour_list.append(s)
        
    dftemp2 = pd.concat(hour_list,axis=1)
    dftemp2['number_agents'] = (dftemp2.sum(axis=1))*2 # Number of hours = number of agents
    df = dftemp2['number_agents']

    df_call = callpatternrange(start='2018-05-01', end='2018-09-15').drop(columns=['Date','rank'])

    df_final = df_call.join(df,how='inner')
    df_final = df_final.drop(columns=['SL Abandoned','Abandoned Calls'])
    df_final = df_final.apply(pd.to_numeric, errors='ignore')
    return df_final

df_final = timeblockrange(start='2018-05-01', end='2018-09-15', exclude=[7356014,7770777,8569433,5806257,8661085,8687861])
df_super = timeblockrange(start='2018-05-01', end='2018-09-15', exclude=[7356014,7770777,5806250,8457625,8661085,8687861])
df_super = df_super.filter(['number_agents']).rename(columns={'number_agents' : 'number_leads'})
df_final = df_final.join(df_super,how='outer').fillna(0)
#df_final = df_final[~(df_final['number_agents'] > 30)]
#df_final = df_final[~(df_final['Overflow Calls'] > 30)]
df_final['ratio'] = df_final['ACD Calls']/df_final['Calls Offered']
df_final['ratio2'] = df_final['number_leads']/df_final['number_agents']
df_final = df_final[(df_final['ratio'] == 1)]
df_final = df_final[~(df_final['ratio2'] > 1)]
#df_final = df_final[~(df_final['Overflow Calls'] > 1)]

# data set-up

x = df_final['Calls Offered'].values
y = df_final['ratio2'].values
slope,intercept,r_value,p_value,std_err = stats.linregress(x,y)
print('y = {0}*x + {1}'.format(slope,intercept))
print('r-squared:',r_value**2)
x_line = [1]*40
y_line = np.arange(0,40).astype('float')
z_line = slope*y_line + intercept

# 3D Scatter-plot with logarithmic fit
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.scatter(df_final['ratio'], df_final['Calls Offered'], df_final['ratio2'], c = df_final['ratio'], marker = 'o', s=10)
ax.plot(x_line, y_line,z_line, color='red', lw=2, label='Lead regression')
plt.title('Shift-Lead Forecasting')
ax.text2D(0.12, -0.1, r'Number of Leads = {0:.3f} * Number of Agents + {1:.3f}'.format(slope,intercept), transform=ax.transAxes)
ax.text2D(0.7, -0.1, r'r-squared = {0:.3f}'.format(r_value**2), transform=ax.transAxes)

ax.set_xlabel('ACD Calls/Offered')
ax.set_ylabel('Calls Offered')
ax.set_zlabel('Leads/Agents')
ax.legend()
