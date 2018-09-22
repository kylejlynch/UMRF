import imaplib, email
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import re
from sensitive import emailcredentials
from custom_functions import get_body,search,get_emails,convtime

user, password, imap_url = emailcredentials()

def agentweekly() :
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    cur = conn.cursor()
    
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Agent Weekly"')
    
    dfemp = pd.DataFrame(columns = ['FirstName','LastName'])
    dfweek = pd.DataFrame()
    datelist = pd.read_sql_query('''SELECT DISTINCT "WeekStart" FROM "AllData"''', conn)['WeekStart'].tolist()
    
    eml = search('Subject','UMRF Agent Stats for the week', mail)[0].split()
    for i in eml[-12:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlhtml = get_body(email.message_from_bytes(data[0][1]))
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('from ([0-9-]+)', soup.text)[0]
        if not dt in datelist :
            print(dt,'not in')
            datelist.append(dt)
            
            #prep/clean data   
            dfraw = pd.read_html(emlhtml,header=0)[0].set_index(['Employee Number'])
            dfraw['IncidentsCreated'] = dfraw['IncidentsCreated'].mask((dfraw['IncidentsCreated'] == 0) & (dfraw['CallsHandled'] > 0))
            dfraw.insert(8, 'Ticket %',((dfraw['IncidentsCreated']/dfraw['CallsHandled'])*100).replace([np.inf,-np.inf], np.nan).round(2))
            dfraw['WeekStart'] = dt
            dfraw['FCR %'] = dfraw['FCR %'].replace({'%' : ''}, regex=True).astype('float')
            dfraw['FCR %'] = dfraw['FCR %'].mask((dfraw['CallsHandled'] == 0))
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
            dfweek = dfweek.append(dfraw)
        else :
            print(dt,'already in')
            continue
    conn2 = sqlite3.connect('emplistmanual.sqlite')
    dfemp = pd.read_sql_query('''SELECT * FROM info''', conn2)
    dfemp = dfemp.filter(['fedex_id','position'])
    dfemp = dfemp[dfemp['position'] == 'Agent']
    dfweek= dfweek.reset_index()
    dfweekly = pd.merge(dfweek,dfemp,left_on='Employee Number',right_on='fedex_id').drop(columns=['fedex_id','position'])
    dfweekly['FCR %'] = dfweekly['FCR %'].mask((dfweekly['FCR %'] == 0) & ~(dfweekly['IncidentsCreated'] > 0))
    dfweekly = dfweekly.sort_values(by=['LastName'])
    dfweekly.to_sql('AllData', conn, if_exists='append',index=False)
    
    conn.commit()
    cur.close()
agentweekly()