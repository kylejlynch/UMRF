# -*- coding: utf-8 -*-
import pandas as pd
import sqlite3
from datetime import date

empid = [3585526,5290664,5289255,5289265,5289275,5290667,5290668,3585532,5291632,5289271,891005,3654246,3654442,3654247,3654240,3654239,3654441,3617735]
def agentdelete() :
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    conn2 = sqlite3.connect('UMRF_SQL_Daily.sqlite')
    cur = conn.cursor()
    cur2 = conn.cursor()
    
    weeklydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn)
    dailydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn2)
    
    if date.today().weekday() != 0 :
        for emp in empid :
            dailydf = dailydf[dailydf['Employee Number'] != emp]
    
    if date.today().weekday() == 0 :
        for emp in empid :
            dailydf = dailydf[dailydf['Employee Number'] != emp]
            weeklydf = weeklydf[weeklydf['Employee Number'] != emp]
    
    weeklydf.to_sql("AllData", conn,if_exists="replace",index=False)
    dailydf.to_sql("AllData", conn2,if_exists="replace",index=False)
    
    conn.commit()
    conn2.commit()
    cur.close()
    cur2.close()