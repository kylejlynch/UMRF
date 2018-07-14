# -*- coding: utf-8 -*-
"""
One time delete from Agent_Weekly and Agent_Daily SQL DBs. Used for old employees and certain dates with bad values
"""
import pandas as pd
import sqlite3

empid = [5289252,3585531,3613787,3617737]
dates = pd.date_range(start='2018-06-17', end='2018-07-08', freq='D').date
print(dates)

def agentonedelete() :
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    conn2 = sqlite3.connect('UMRF_SQL_Daily.sqlite')
    cur = conn.cursor()
    cur2 = conn2.cursor()
    
    weeklydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn)
    dailydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn2)
    
    for emp in empid :
        dailydf = dailydf[dailydf['Employee Number'] != emp]
        weeklydf = weeklydf[weeklydf['Employee Number'] != emp]
    
    for dt in dates :
        dt = str(dt)
        dailydf = dailydf[dailydf['Date'] != dt]
        weeklydf = weeklydf[weeklydf['WeekStart'] != dt]
        
    weeklydf.to_sql("AllData", conn,if_exists="replace",index=False)
    dailydf.to_sql("AllData", conn2,if_exists="replace",index=False)
    
    conn.commit()
    conn2.commit()
    cur.close()
    cur2.close()
agentonedelete()