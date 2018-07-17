# -*- coding: utf-8 -*-
'''
1. Retrieves number of offered calls, accepted calls, and overflow (missed) calls over a given period
2. Retrieves start/end times for agents each day in given time period
3. Predicts the minimum number of agents needed to accept all calls to take call flow based on data in the
    given time period using various Scikit-Learn regression methods
4. Produces 3d plot for visualization
'''
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
import matplotlib.pyplot as plt
from sensitive import wheniworktoken
from custom_functions import ampmtime
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from sklearn.svm import SVR
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 300)

def callpattern() :
    df = pd.DataFrame()
    datelist = []
    days = {'Monday':int(0), 'Tuesday':int(1), 'Wednesday':int(2), 'Thursday':int(3), 'Friday':int(4), 'Saturday':int(5), 'Sunday':int(6)}
    
    #path = 'Call Patterns/June2018/'
    #listing = os.listdir(path)
    #for file in listing :
    for root, dirs, files in os.walk('Call Patterns/') :
        for file in files :
            #fh = open(os.path.join(path,file), 'rb')
            fh = open(os.path.join(root,file), 'rb')
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
            year, month, day = dt.split('-')
            day = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
            if dt not in datelist :
                datelist.append(dt)
            
                #prep/clean data
                dfraw = pd.read_html(emlhtml,header=0)[0]
                dfraw = dfraw.iloc[14:40].reset_index(drop=True)
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
                dfraw = dfraw.reset_index(drop=True)
                dfraw['Day'] = day
                dfraw = dfraw.reset_index(drop=True)
                dfraw['Time Interval'] = pd.date_range(start='{} 07:30:00'.format(dt), end='{} 20:00:00'.format(dt), freq='30T').astype('str')
                dfraw = dfraw.set_index(['Time Interval'])
                dfraw['Percent_ACD'] = (dfraw['ACD Calls'].astype('int')/dfraw['Calls Offered'].astype('int')).replace([np.inf,-np.inf],np.nan).fillna(0)
                df = df.append(dfraw)
            else : continue
    df_call = df.apply(pd.to_numeric, errors='ignore')
    return df_call

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

    df_call = callpattern()

    #df_final = pd.concat([df,df_call], axis=1).fillna(0)
    df_final = df_call.join(df,how='inner')
    df_final = df_final.drop(columns=['SL Abandoned','Abandoned Calls'])
    return df_final

    year, month, day = start.split('-')
    dayname = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
    month = calendar.month_name[int(month)]
df_final = timeblockrange(start='2018-05-01', end='2018-06-26', exclude=[7356014,8569433,5806257])

X = df_final[['Calls Offered','Percent_ACD']].values.reshape(-1,2)
y = df_final['number_agents'].values.reshape(-1,1)

X_train, X_test, y_train, y_test = train_test_split(X,y,random_state = 0)
linreg = linear_model.LinearRegression().fit(X_train,y_train)
print(linreg.score(X_train,y_train))
print(linreg.score(X_test,y_test))
linreg = linear_model.Lasso().fit(X_train,y_train)
print(linreg.score(X_train,y_train))
print(linreg.score(X_test,y_test))
linreg = linear_model.BayesianRidge().fit(X_train,y_train)
print(linreg.score(X_train,y_train))
print(linreg.score(X_test,y_test))
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1).fit(X_train,y_train)
print(svr_rbf.score(X_train,y_train))
print(svr_rbf.score(X_test,y_test))

print('##################')
clf = linear_model.LinearRegression()
clf.fit(X, y)
print('Least Squared',clf.predict([[30, 0.98]]))
clf = linear_model.Lasso()
clf.fit(X, y)
print('Lasso',clf.predict([[30, 0.98]]))
clf = linear_model.BayesianRidge()
clf.fit(X, y)
print('Ridge',clf.predict([[30, 0.98]]))
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
y_rbf = svr_rbf.fit(X, y).predict([[30,0.98]])
print('SVR',y_rbf)

#cmap = cm.get_cmap('gnuplot')
#scatter = pd.plotting.scatter_matrix(df_final[['Calls Offered','Percent_ACD','number_agents']], c= df_final['number_agents'], marker = 'o', s=40, hist_kwds={'bins':15}, figsize=(9,9), cmap=cmap)

# plotting a 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.scatter(df_final['Calls Offered'], df_final['number_agents'], df_final['Percent_ACD'], c = df_final['number_agents'], marker = 'o', s=30)
ax.set_xlabel('Calls Offered')
ax.set_ylabel('Number of Agents')
ax.set_zlabel('Percent ACD')
