# -*- coding: utf-8 -*-
"""
Obtains performance data from previous week, syncs to employee info
used to send performance data separately to all employees
"""
import pandas as pd
import sqlite3
from datetime import datetime,timedelta

pd.set_option('display.max_columns', 100)

def agentprevweekemail() :
    conn1 = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    conn2 = sqlite3.connect('emplist.sqlite')
    dfweek = pd.read_sql('''SELECT * FROM AllData''', conn1)
    dfweek = dfweek[dfweek['WeekStart'] == dfweek['WeekStart'].max()]
    start = dfweek['WeekStart'].iloc[0]
    end = datetime.strftime(datetime.strptime(start,'%Y-%m-%d') + timedelta(7), '%Y-%m-%d')
    dfweek['DateRange'] = '{0} to {1}'.format(start,end)
    dfweek = dfweek.filter(['DateRange','FirstName','LastName','FCR %','CallsHandled','AHT (min)','Ticket %','IncidentsCreated','IncidentsCreatedAndResolved','Number of Surveys','Avg. Survey Score (100)'])
    dfweek = dfweek.rename(columns={'FCR %' : 'Call Resolution %','AHT (min)' : 'Avg Handle Time (min)'})
    dfemp = pd.read_sql('''SELECT * FROM info''', conn2)
    dfemp = dfemp.filter(['first_name','last_name','email']).rename(columns={'first_name':'FirstName','last_name':'LastName'})
    df = pd.merge(dfweek,dfemp, on=['FirstName','LastName'])
    for i,row in df.iterrows() :
        dfagent = pd.DataFrame(row).rename(columns={i:'Agent Stats'})
        print(dfagent)
        dfagent.to_html('weekly_stats.html')
        
agentprevweekemail()