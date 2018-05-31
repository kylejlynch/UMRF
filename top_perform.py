# -*- coding: utf-8 -*-
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, date

def top_perform() :
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    cur = conn.cursor()
    conn2 = sqlite3.connect('UMRF_SQL_Daily.sqlite')
    cur = conn2.cursor()
    
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    lstwk = datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d')
    
    val = ['FCR %', 'NR%', 'AHT (min)',"IncidentsCreated"]
    order = ['DESC','ASC','ASC','DESC']
    file = ['dayFCR','dayNR','dayAHT','dayINC']
    for i,j,k in zip(val,order,file) :
        topdf = pd.read_sql_query('''SELECT "FirstName",
                                         "LastName",
                                         "{0}"
                                         FROM "AllData"
                                         WHERE "Date"
                                         IS "{1}"
                                         AND "IncidentsCreated" > 5
                                         ORDER BY "{0}" {2} LIMIT 3'''.format(i,yesterday,j),
                                         conn2)
        topdf.index += 1
        topdf.to_html('{}.html'.format(k))
    
    if date.today().weekday() == 0 :
        val = ['FCR %', 'NR%', 'AHT (min)',"IncidentsCreated"]
        order = ['DESC','ASC','ASC','DESC']
        file = ['weekFCR','weekNR','weekAHT','weekINC']
        for i,j,k in zip(val,order,file) :
            topdf = pd.read_sql_query('''SELECT "FirstName",
                                             "LastName",
                                             "{0}"
                                             FROM "AllData"
                                             WHERE "WeekStart"
                                             IS "{1}"
                                             AND "IncidentsCreated" > 20
                                             ORDER BY "{0}" {2} LIMIT 3'''.format(i,lstwk,j),
                                             conn)
            topdf.index += 1
            topdf.to_html('{}.html'.format(k))
    
    conn.commit()
    cur.close()
