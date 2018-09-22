# -*- coding: utf-8 -*-
import imaplib, email
import sqlite3
import pandas as pd
import numpy as np
import os
import re
from datetime import date,datetime,timedelta
import calendar
from sensitive import emailcredentials
from custom_functions import get_body,search,get_emails,convtime
from io import StringIO
from UMRF_send_report import send_mail

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_colwidth', -1)

def rejectedincidents() :
    today = datetime.strftime(datetime.today(), '%Y-%m-%d')
    yesterday = datetime.strftime(datetime.strptime(today,'%Y-%m-%d') - timedelta(1), '%d-%b-%Y')
    print(yesterday)

    conn = sqlite3.connect('UMRF_Incidents_SQL.sqlite')
    conn2 = sqlite3.connect('emplistmanual.sqlite')
    dflist = []
    
    user, password, imap_url = emailcredentials()
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(user,password)
    mail.select('"Rejected Incidents"')
    
    eml = search('ON', "{}".format(yesterday), mail)[0].split()
    for i in eml[:] :
        result, data = mail.fetch(i,'(RFC822)')
        emlbytes = get_body(email.message_from_bytes(data[0][1]))
        try :
            s = str(emlbytes,'windows-1252')
            incidentNum = re.findall('Incident # (INC[0-9]+)', s)[0]
        except :
            print('multipart email: trying base64 decoding')
        try :
            b = email.message_from_bytes(data[0][1])
            if b.is_multipart():
                for part in b.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
            
                    # skip any text/plain (txt) attachments
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        s = part.get_payload(decode=True)  # decode
                        break
            else :
                s = b.get_payload(decode=True)
        except :
            print('could not read, fetching incident number from subject...')
            s = str(data[0][1])[2:-1]
        s = str(s,'windows-1252')
        
        incidentNum = re.findall('Incident (INC[0-9]+)', s)[0]
        sql = '''SELECT * FROM AllData
                WHERE number IS "{}"'''.format(incidentNum)
        dfraw = pd.read_sql_query(sql,conn)
        df = dfraw.replace({'\r\n':'. ','\n':' '}, regex=True)
        df = df.filter(['number','sys_created_by','opened_by','opened_at','company','assignment_group','reassignment_count','u_resolving_level','resolved_by','short_description','description','comments_and_work_notes','close_notes'])
        df = df.rename(columns={'sys_created_by':'Emp_ID','reassignment_count':'reassigned','u_resolving_level':'resolving_lvl'})
        #df = df.drop(columns=['comments_and_work_notes','comments'])
        #print(df)
        dflist.append(df)
        
    if len(dflist) > 1 :
        df = pd.concat(dflist,axis=0)
        df = df.apply(pd.to_numeric, errors='ignore')
    elif len(dflist) == 1 :
        df = df.apply(pd.to_numeric, errors='ignore')
    elif len(dflist) == 0 :
        print('No Rejected Incidents!')
    try :
        df.to_html('rejected_incidents_yest.html',index=False)
        dfempcount = pd.read_sql_query('''SELECT * FROM "EmpCount"''', conn, index_col=None)
        dfcount = df.filter(['number','Emp_ID'])
        dfempcount = dfempcount.append(dfcount,sort=False)
        dfempcount = dfempcount.drop_duplicates(subset=['number'])
        dfempcount.to_sql('EmpCount', conn, if_exists='replace',index=False)
        df = df.drop(columns=['Emp_ID'])
        dfemp = pd.read_sql_query('''SELECT * FROM info''', conn2)
        df_emp = dfemp.filter(['email2','position'])
        df_emp = df_emp[~(df_emp['position'] == 'Agent')]
        eml = df_emp['email2'].values.tolist()
        html = StringIO()
        df.to_html(buf=html)
        dfhtml = pd.read_html(html,index_col=0)[0]
        print(eml)
        html = dfhtml.to_html(border='border',index=False)
        
        text = '''This is an automated email. If you have any questions, concerns, or feedback please email Kyle Lynch at kylejlynch@gmail.com'''
                
        #send_mail(user, eml,'Rejected Incidents Report for {}'.format(yesterday), text=text, html=html)
    except :
        print('No Rejected Incidents!')
    print('UMRF_Rejected_Incidents.py completed successfully!')
rejectedincidents()