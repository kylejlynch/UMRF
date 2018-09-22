# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 22:35:56 2018

@author: Labuser
"""

import imaplib, email
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import re
from datetime import date
import calendar
from sensitive import emailcredentials
from custom_functions import get_body,search,get_emails,convtime
from io import StringIO

pd.set_option('display.max_columns', 100)

def agentdailycsv() :

    conn = sqlite3.connect('UMRF_Incidents_SQL.sqlite')
    dflist = []
    days = {'Monday':int(0), 'Tuesday':int(1), 'Wednesday':int(2), 'Thursday':int(3), 'Friday':int(4), 'Saturday':int(5), 'Sunday':int(6)}
    try :
        datelist = pd.read_sql_query('''SELECT DISTINCT "Date" FROM "AllData"''', conn)['Date'].tolist()
    except :
        datelist = []
    
    user, password, imap_url = emailcredentials()
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Incidents Daily"')
    
    eml = search('Subject','FW: UMRF_Incidents', mail)[0].split()
    for i in eml[-5:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlbytes = get_body(email.message_from_bytes(data[0][1]))
        #print(emlbytes)
        s = str(emlbytes,'windows-1252')
        #print(s)
        data = StringIO(s)
        df = pd.read_csv(data)
        df = df.filter(['number','opened_at','u_affected_user','short_description','state','assignment_group','assigned_to','caller_id.user_name','category','business_service','work_notes','urgency','severity','resolved_at','close_notes','reopen_count','reassignment_count','priority','parent_incident','incident_state','impact','calendar_duration','description','sys_created_by','sys_created_on','correlation_display','location','comments_and_work_notes','closed_at','comments','active','resolved_by','opened_by','cmdb_ci','company','u_resolving_level','u_process_feedback','u_process_feedback_notes'])
        dt = df.at[2, 'opened_at'][:10]
        year, month, day = dt.split('-')
        day = calendar.day_name[calendar.weekday(int(year), int(month), int(day))]
        if dt not in datelist :
            print(dt,'not in')
            datelist.append(dt)
            df['Date'] = dt
            dflist.append(df)
        else :
            print(dt,'already in')
            continue
    if len(dflist) > 1 :
        dfall = pd.concat(dflist,axis=0).sort_values(by=['Date'],kind='mergesort')
        dfall = dfall.apply(pd.to_numeric, errors='ignore')
        dfall.to_sql('AllData', conn, if_exists='append')
    elif len(dflist) == 1 :
        df = df.apply(pd.to_numeric, errors='ignore')
        df.to_sql('AllData', conn, if_exists='append')
    elif len(dflist) == 0 :
        print('Already up to date!')
    print('UMRF_Incident_Daily_SQL.py completed successfully!')
agentdailycsv()