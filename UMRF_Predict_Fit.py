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

    df_call = callpatternrange(start='2018-05-01', end='2018-07-22').drop(columns=['Date','rank'])

    #df_final = pd.concat([df,df_call], axis=1).fillna(0)
    df_final = df_call.join(df,how='inner')
    df_final = df_final.drop(columns=['SL Abandoned','Abandoned Calls'])
    df_final = df_final.apply(pd.to_numeric, errors='ignore')
    return df_final

df_final = timeblockrange(start='2018-05-01', end='2018-07-22', exclude=[7356014,8569433,5806257,8661085])
df_final = df_final[~(df_final['number_agents'] > 30)]
df_final = df_final[~(df_final['Overflow Calls'] > 30)]
#df_final = df_final[~(df_final['Overflow Calls'] == 0)]

# data set-up
x = np.array([df_final['Calls Offered'].tolist(),df_final['Overflow Calls'].tolist()],dtype=float) # x, y axes
z = np.array(df_final['number_agents'].tolist(),dtype=float) # z axis

# define function
def logfit(x, a, b, c, d) :
    return a * np.log(b*x[0] + c*x[1] + d)
guess = (20,1,5,1) # initial guess at constants a,b,c and d
popt, pcov = curve_fit(logfit, x, z, guess)
print('a = {0} , b = {1}, c = {2}, d = {3}'.format(popt[0], popt[1], popt[2], popt[3]))
print('z = {0}*ln({1}*x + {2}*y + {3})'.format(popt[0],popt[1],popt[2],popt[3]))

# r-squared value
residuals = z - logfit(x, popt[0], popt[1], popt[2], popt[3])
ss_res = np.sum(residuals**2)
ss_tot = np.sum((z - np.mean(z))**2)
r_squared = 1 - (ss_res / ss_tot)
print(r_squared)

# Plot log set-up
x_line = np.arange(0,50).astype('float')
y_line = [1]*50
y_range =np.arange(0,50).astype('float')
XX = pd.DataFrame({'x':x_line.tolist(),'y':y_line})

# KNN, Neural Network & plot set-up
X = df_final[['Calls Offered','Overflow Calls']].values.reshape(-1,2)
y = df_final['number_agents'].values.reshape(-1,1)

y_knn = KNeighborsRegressor(n_neighbors=20).fit(X,y).predict(XX) #KNN
#nn = MLPRegressor(hidden_layer_sizes=(30), activation='tanh',max_iter=300).fit(X, y).predict(XX)
nn = MLPRegressor(hidden_layer_sizes=(5), activation='tanh',solver='lbfgs').fit(X, y).predict(XX) # Neural Network


def nnfit(data) :
    data = [data]
    X = df_final[['Calls Offered','Overflow Calls']].values.reshape(-1,2)
    y = df_final['number_agents'].values.reshape(-1,1)
    nn = MLPRegressor(hidden_layer_sizes=(5), activation='tanh',solver='lbfgs').fit(X, y).predict(data)
    return nn

# 3D Scatter-plot with logarithmic fit
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.scatter(df_final['Calls Offered'], df_final['Overflow Calls'], df_final['number_agents'], c = df_final['number_agents'], marker = 'o', s=30)
ax.plot(x_line, y_line, popt[0]*np.log(popt[1]*XX['x']+ popt[2]*XX['y'] + popt[3]), color='r', label='Logarithmic reg')
#ax.plot(x_line, y_line, y_knn.ravel(), color='navy', lw=2, label='KNN model')
ax.plot(x_line, y_line, nn.ravel(), color='navy', lw=2, label='Neural Network MLP reg')
X, Y = np.meshgrid(x_line, y_range)
Z = popt[0]*np.log(popt[1]*X + popt[2]*Y + popt[3])
X[X>50]= np.nan; X[X<0]= np.nan
Y[Y>15]= np.nan; Y[Y<0]= np.nan
Z[Z>35]= np.nan; Z[Z<0]= np.nan
ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False, alpha=0.5, vmin=0, vmax=30)
plt.title('Agent Forecasting')
ax.text2D(0.0, -0.1, r'Num of agents = {0:.3f} * ln({1:.3f} * x + {2:.3f} * y + {3:.3f})'.format(popt[0], popt[1], popt[2], popt[3]), transform=ax.transAxes)
ax.text2D(0.8, -0.1, r'r-squared = {0:.3f}'.format(r_squared), transform=ax.transAxes)
ax.set_xlabel('Calls Offered')
ax.set_ylabel('Overflow Calls')
ax.set_zlabel('Number of Agents')
ax.legend()

