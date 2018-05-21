import pandas as pd
import sqlite3

weeklist = ['2018-04-09','2018-04-02'] #Weeks needing correction

conn = sqlite3.connect('UMRF_SQL_Daily.sqlite')
cur = conn.cursor()
conn2 = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
cur2 = conn2.cursor()

emplist = pd.read_sql_query('''SELECT DISTINCT "Employee Number" FROM "AllData"''', conn)['Employee Number'].tolist()

weeklydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn2)

for week in weeklist :
    sql = '''SELECT
        "Employee Number","LastName","FirstName",
        sum("Number of Surveys") AS "Number of Surveys",
        round(sum("Avg. Survey Score (100)"*"Number of Surveys")/sum("Number of Surveys"),2) AS "Avg. Survey Score (100)",
        round(sum("Avg. Survey Score (5)"*"Number of Surveys")/sum("Number of Surveys"),2) AS "Avg. Survey Score (5)",
        sum(IncidentsCreated) AS "IncidentsCreated",
        sum(IncidentsCreatedAndResolved) AS "IncidentsCreatedAndResolved",
        round(sum("FCR %"*"IncidentsCreated")/sum("IncidentsCreated"),2) AS "FCR %",
        round(sum("Ticket %"*"CallsHandled")/sum(1.0*"CallsHandled"),2) AS "Ticket %",
        sum(IncidentsResolved) AS "IncidentsResolved",
        sum("LoggedOnTime (hrs)") AS "LoggedOnTime (hrs)",
        sum("AvailTime (hrs)") AS "AvailTime (hrs)",
        sum("NotReadyTime (hrs)") AS "NotReadyTime (hrs)",
        round(sum("NotReadyTime (hrs)")/sum("LoggedOnTime (hrs)")*100,2) AS "NR%",
        sum("CallsAnswered") AS "CallsAnswered",
        round(sum("ACH%"*"LoggedOnTime (hrs)")/sum("LoggedOnTime (hrs)"),2) AS "ACH%",
        round(sum("ASA (min)"*"CallsHandled")/sum("CallsHandled"),2) AS "ASA (min)",
        sum("CallsHandled") AS "CallsHandled",
        round(sum("AHT (min)"*"CallsHandled")/sum("CallsHandled"),2) AS "AHT (min)",
        sum("AbandonRingCalls") AS "AbandonRingCalls",
        sum("AbandonHoldCalls") AS "AbandonHoldCalls",
        sum("AbandonHoldOutCalls") AS "AbandonHoldOutCalls",
        sum("ShortCalls") AS "ShortCalls",
        max(date(Date, 'weekday 0', '-6 day')) AS "WeekStart"
        FROM "AllData"
        WHERE date(Date, 'weekday 0', '-6 day') IS "{}"
        GROUP BY "Employee Number"'''.format(week)
    tempdf = pd.read_sql_query(sql,conn)
    weeklydf = weeklydf.append(tempdf).drop_duplicates(['Employee Number','WeekStart'],keep='last')

weeklydf[['Avg. Survey Score (100)','Avg. Survey Score (5)']] = weeklydf[['Avg. Survey Score (100)','Avg. Survey Score (5)']].fillna(value=int(0))
weeklydf = weeklydf.sort_values(by=['WeekStart', 'LastName'])

weeklydf.to_sql("AllData", conn2,if_exists="replace",index=False)

conn.commit()
conn2.commit()
cur.close()
cur2.close()