import imaplib, email
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import re
from sensitive import emailcredentials

user, password, imap_url = emailcredentials()

def get_body(msg) :
    if msg.is_multipart() :
        return get_body(msg.get_payload(1))
    else :
        return msg.get_payload(None,True)

def search(key,value,conn) :
    result, data = conn.search(None,key,'"{}"'.format(value))
    return data

def get_emails(result_bytes) :
    msgs = []
    for num in result_bytes[0].split() :
        typ, data = conn.fetch(num, '(RFC822)')
        msgs.append(data)
        return msgs

def convtime(t) :
    h,m,s = re.split(':',t)
    _hrs = int(h) + int(m)/60 + int(s)/3600
    _min = int(h)*60 + int(m) + int(s)/60
    return '{:.3f}'.format(_hrs),'{:.3f}'.format(_min)

def agentweekly() :
    conn = sqlite3.connect('UMRF_SQL_Weekly.sqlite')
    cur = conn.cursor()
    
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Agent Weekly"')
    
    dfemp = pd.DataFrame(columns = ['FirstName','LastName'])
    dfdaily = pd.DataFrame()
    datelist = pd.read_sql_query('''SELECT DISTINCT "WeekStart" FROM "AllData"''', conn)['WeekStart'].tolist()
    
    eml = search('Subject','UMRF Agent Stats for the week', mail)[0].split()
    for i in eml[-2:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlhtml = get_body(email.message_from_bytes(data[0][1]))
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('from ([0-9-]+)', soup.text)[0]
        if not dt in datelist :
            print(dt,'not in')
            datelist.append(dt)
            
            #prep/clean data   
            dfraw = pd.read_html(emlhtml,header=0)[0].set_index(['Employee Number'])
            dfraw.insert(8, 'Ticket %',((dfraw['IncidentsCreated']/dfraw['CallsHandled'])*100).replace([np.inf,-np.inf], np.nan).round(2))
            dfraw['WeekStart'] = dt
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
        else :
            print(dt,'already in')
            continue
    
    dfdaily.to_sql('AllData', conn, if_exists='append')
    
    conn.commit()
    cur.close()
