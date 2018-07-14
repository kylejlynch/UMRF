import pandas as pd
import sqlite3

weeklist = ['2018-04-09','2018-04-02'] #Weeks needing correction

conn = sqlite3.connect('UMRF_SQL_Daily.sqlite')
cur = conn.cursor()
conn2 = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
cur2 = conn2.cursor()

dailydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn)
weeklydf = pd.read_sql_query('''SELECT * FROM "AllData"''', conn2)

dailydf['FirstName'] = dailydf['FirstName'].replace(to_replace='Nicolas', value='Nicholas')
dailydf['LastName'] = dailydf['LastName'].replace(to_replace='Macklin', value='Maclin')
weeklydf['FirstName'] = weeklydf['FirstName'].replace(to_replace='Nicolas', value='Nicholas')
weeklydf['LastName'] = weeklydf['LastName'].replace(to_replace='Macklin', value='Maclin')

dailydf.to_sql("AllData", conn,if_exists="replace",index=False)
weeklydf.to_sql("AllData", conn2,if_exists="replace",index=False)

conn.commit()
conn2.commit()
cur.close()
cur2.close()
