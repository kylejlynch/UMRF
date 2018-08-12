# -*- coding: utf-8 -*-
"""
Calculates average callflow/outflow for a specified range of dates from SQL database
"""
import pandas as pd
import sqlite3
import numpy as np
import string

pd.set_option('display.max_columns', 100)

def callpatternrange(start, end) :
    start = start
    end = end
    conn = sqlite3.connect('UMRF_Call_Pattern.sqlite')
    datelist = pd.date_range(start=start,end=end,freq='D')
    datelist = datelist.strftime('%Y-%m-%d').tolist()

    dfsql = pd.read_sql('''
                        SELECT *
                        FROM AllData
                        ''', conn, index_col='Time Interval')
    df_range = dfsql[dfsql['Date'].isin(datelist)]
    return df_range

'''
df = callpatternrange(start, end)
df = df.apply(pd.to_numeric, errors='ignore')
dfavg = df.groupby(['rank','Day','Time Interval'],sort=False)['Calls Offered','Overflow Calls'].mean()
dfavg['Calls stdev'] = df.groupby(['rank','Day','Time Interval'],sort=False)['Calls Offered'].agg(np.std, ddof=0)
dfavg['Overflow stdev'] = df.groupby(['rank','Day','Time Interval'],sort=False)['Overflow Calls'].agg(np.std, ddof=0)
dfavg['Pred Num Agents'] = dfavg['Calls Offered']/1.32
dfavg = dfavg.round(3)

dfavg = dfavg.apply(pd.to_numeric, errors='ignore')
dfavg = dfavg.sort_index(level=0,sort_remaining=False).reset_index(level=0,drop=True)
print(dfavg)
writer = pd.ExcelWriter('Avg_Callflow_July01to18.xlsx')
dfavg.to_excel(writer,'Sheet1')
worksheet = writer.sheets['Sheet1']
letters = list(string.ascii_uppercase)
for i,col in enumerate(list(dfavg.reset_index())) :    #autofit column-width
    worksheet.set_column('{}:{}'.format(letters[i],letters[i]), max(12,len('{}'.format(col))+2,dfavg.reset_index()['{}'.format(col)].astype(str).map(len).max()+2))
writer.save()
'''