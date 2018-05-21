import sqlite3
import pandas as pd
import numpy as np
import os
import re
from bs4 import BeautifulSoup
import email

conn = sqlite3.connect('UMRF_SQL_Daily.sqlite')
cur = conn.cursor()

def convtime(t) :
    h,m,s = re.split(':',t)
    _hrs = int(h) + int(m)/60 + int(s)/3600
    _min = int(h)*60 + int(m) + int(s)/60
    return '{:.3f}'.format(_hrs),'{:.3f}'.format(_min)

dfemp = pd.DataFrame(columns = ['FirstName','LastName'])
dfdaily = pd.DataFrame()
datelist = []

path = 'Agent_Daily/'
listing = os.listdir(path)
for file in listing :
    fh = open(os.path.join(path,file), 'rb')
    handle = email.message_from_string(fh.read().decode())
    if handle.is_multipart() :
        for part in handle.walk() :
            if part.get_content_type() == 'text/html' :
               emlhtml = part.get_payload(decode=True).decode()
    else :
        emlhtml = handle.get_payload()
               
    #extract data
    soup = BeautifulSoup(emlhtml, 'lxml')
    dt = re.findall('from ([0-9-]+)', soup.text)[0]
    if dt not in datelist :
        datelist.append(dt)
        
        #prep/clean data   
        dfraw = pd.read_html(emlhtml,header=0)[0].set_index(['Employee Number'])
        dfraw.insert(8, 'Ticket %',((dfraw['IncidentsCreated']/dfraw['CallsHandled'])*100).replace([np.inf,-np.inf], np.nan).round(2))
        dfraw['Date'] = dt
        dfraw['FCR %'] = dfraw['FCR %'].replace({'%' : ''}, regex=True).astype('float')
        dfraw['LoggedOnTime'] = dfraw['LoggedOnTime'].apply(lambda x : float(convtime(x)[0]))
        dfraw['AvailTime'] = dfraw['AvailTime'].apply(lambda x : float(convtime(x)[0]))
        dfraw['NotReadyTime'] = dfraw['NotReadyTime'].apply(lambda x : float(convtime(x)[0]))
        dfraw['ASA'] = dfraw['ASA'].apply(lambda x : float(convtime(x)[1]))
        dfraw['AHT'] = dfraw['AHT'].apply(lambda x : float(convtime(x)[1]))
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
        dfemp.index.rename('Employee Number',inplace=True)
        dfdaily = dfdaily.append(dfraw)
    else : continue

dfdaily.to_sql('AllData', conn, if_exists='append')

conn.commit()
cur.close()