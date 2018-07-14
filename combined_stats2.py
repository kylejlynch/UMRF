# -*- coding: utf-8 -*-
import imaplib, email
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import re
from datetime import date, datetime
from sensitive import emailcredentials

pd.set_option('display.max_columns', 100)

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

def combinedstats() :
    #conn = sqlite3.connect('UMRF_SQL_Daily.sqlite')
    #cur = conn.cursor()
    
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Combined Stats"')
    
    #datelist = pd.read_sql_query('''SELECT DISTINCT "Date" FROM "AllData"''', conn)['Date'].tolist()
    
    eml = search('Subject','Combined L1 UMRF Stats', mail)[0].split()
    dflist = []
    for i in eml :
    #for i in eml[-5:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlhtml = get_body(email.message_from_bytes(data[0][1]))
        soup = BeautifulSoup(emlhtml, 'lxml')
        dt = re.findall('for ([0-9-]+)', soup.text)[0]
        dt = datetime.strptime(dt, "%Y-%m-%d")
        dfraw = pd.read_html(emlhtml,header=1)[0]
        dfraw['Date'] = dt
        dfdata = dfraw.filter(['Service Desk','Date','Calls Offered','Calls Answered','Calls Abandoned', 'Calls Flow Out'])
        dfdata = dfdata[dfdata['Service Desk'] == 'UMRF']
        dflist.append(dfdata)
    df = pd.concat(dflist)
    df = df.sort_values(by = 'Date').reset_index()
    print(df)

combinedstats()