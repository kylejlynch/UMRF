import sqlite3
import pandas as pd
import os
import time
import re

conn = sqlite3.connect('UMRF_SQL.sqlite')
cur = conn.cursor()

def convtime(t) :
    h,m,s = re.split(':',t)
    _hrs = int(h) + int(m)/60 + int(s)/3600
    _min = int(h)*60 + int(m) + int(s)/60
    return '{:.3f}'.format(_hrs),'{:.3f}'.format(_min)
dfemp = pd.DataFrame(columns = ['FirstName','LastName'])

path = 'data/'
listing = os.listdir(path)
for file in listing :
    handle = open(os.path.join(path,file) , 'r')
    #extract data
    dfraw = pd.read_csv(handle).set_index(['Employee Number'])
    dfraw['FileDate'] = time.strftime('%m/%d/%Y', time.gmtime(os.path.getctime(os.path.join(path,file))))
    dfraw['LoggedOnTime'] = dfraw['LoggedOnTime'].apply(lambda x : convtime(x)[0])
    dfraw['AvailTime'] = dfraw['AvailTime'].apply(lambda x : convtime(x)[0])
    dfraw['NotReadyTime'] = dfraw['NotReadyTime'].apply(lambda x : convtime(x)[0])
    dfraw['ASA'] = dfraw['ASA'].apply(lambda x : convtime(x)[1])
    dfraw['AHT'] = dfraw['AHT'].apply(lambda x : convtime(x)[1])
    dfraw.rename(columns = {
                            'LoggedOnTime':'LoggedOnTime (hrs)',
                            'AvailTime' : 'AvailTime (hrs)',
                            'NotReadyTime' : 'NotReadyTime (hrs)',
                            'ASA' : 'ASA (min)',
                            'AHT' : 'AHT (min)',
                            }
                ,inplace=True)
    dftemp = dfraw.filter(items = ['FirstName','LastName'])
    dfemp = dfemp.append(dftemp)
    dfemp.drop_duplicates(inplace=True)
    dfemp.index.names = ['Employee Number']
    for i in dfraw.index :
        (dfraw.loc[[i]]).to_sql('{} {} {}'.format(i,dfraw.at[i,'FirstName'],dfraw.at[i,'LastName']), conn, if_exists="append")

dfcols = pd.DataFrame(columns = dfraw.reset_index().columns.values).drop(['FileDate'],axis=1)
dfcols.set_index(['Employee Number']).to_sql('Summary', conn, if_exists="append")

for i in dfemp.index :
    emp = '{} {} {}'.format(i,dfemp.at[i,'FirstName'],dfemp.at[i,'LastName'])
    cur.execute('''INSERT INTO Summary
                SELECT "Employee Number" AS "Employee Number",
                "LastName" AS "LastName",
                "FirstName" AS "FirstName",
                sum("Number of Surveys") AS "Number of Surveys",
                sum("Number of Surveys"*"Avg. Survey Score (100)")/sum("Number of Surveys") AS "Avg. Survey Score (100)",
                sum("Number of Surveys"*"Avg. Survey Score (5)")/sum("Number of Surveys") AS "Avg. Survey Score (5)",
                sum("IncidentsCreated") AS "IncidentsCreated",
                sum("IncidentsCreatedAndResolved") AS "IncidentsCreatedAndResolved",
                (sum(CAST("IncidentsCreatedAndResolved" AS float))/sum(CAST("IncidentsCreated" AS float)))*100 AS "FCR %",
                sum("IncidentsResolved") AS "IncidentsResolved",
                avg("LoggedOnTime (hrs)") AS "LoggedOnTime (hrs)",
                avg("AvailTime (hrs)") AS "AvailTime (hrs)",
                avg("NotReadyTime (hrs)") AS "NotReadyTime (hrs)",
                (sum(CAST("NotReadyTime (hrs)" AS float))/sum(CAST("LoggedOnTime (hrs)" AS float)))*100 AS "NR %", 
                sum("CallsAnswered") AS "CallsAnswered",
                (sum("CallsAnswered")/sum(CAST("LoggedOnTime (hrs)" AS float))) AS "ACH %",
                avg("ASA (min)") AS "ASA (min)",
                sum("CallsHandled") AS "CallsHandled", 
                sum("AHT (min)"*"CallsHandled")/sum("CallsHandled") AS "AHT (min)",
                sum("AbandonRingCalls") AS "AbandonRingCalls",
                sum("AbandonHoldCalls") AS "AbandonHoldCalls",
                sum("AbandonHoldOutCalls") AS "AbandonHoldOutCalls",
                sum("ShortCalls") AS "ShortCalls"
                FROM "{}" ''' .format(emp))

conn.commit()

cur.close()